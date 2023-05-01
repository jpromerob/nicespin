#include <iostream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <chrono>
#include <thread>
#include <cstring>
#include <arpa/inet.h> // Add this header
#define BUFFER_SIZE 1024

int main(int argc, char *argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " packet_size" << std::endl;
        return 1;
    }

    const int packet_size = std::stoi(argv[1]);

    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        std::cerr << "Failed to create socket" << std::endl;
        return 1;
    }

    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(3333);
    inet_pton(AF_INET, "172.16.223.10", &server_addr.sin_addr);

    client_addr.sin_family = AF_INET;
    client_addr.sin_port = htons(3332);
    client_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(sockfd, (struct sockaddr*)&client_addr, sizeof(client_addr)) < 0) {
        std::cerr << "Failed to bind socket to local address" << std::endl;
        return 1;
    }

    char buffer[BUFFER_SIZE];

    while (true) {
        // Send packet
        memset(buffer, 0, BUFFER_SIZE);
        if (sendto(sockfd, buffer, packet_size, 0, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
            std::cerr << "Failed to send packet" << std::endl;
            return 1;
        }

        // Receive packet
        memset(buffer, 0, BUFFER_SIZE);
        if (recvfrom(sockfd, buffer, BUFFER_SIZE, 0, (struct sockaddr*)&client_addr, &client_len) < 0) {
            std::cerr << "Failed to receive packet" << std::endl;
            return 1;
        }

        // Sleep for 2 seconds
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }

    return 0;
}