#include <iostream>
#include <string.h>
#include <chrono>
#include <thread>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

int main() {


           

    int sockfd;
    struct sockaddr_in servaddr, cliaddr;

    // Creating socket file descriptor
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);

    memset(&servaddr, 0, sizeof(servaddr));
    memset(&cliaddr, 0, sizeof(cliaddr));

    // Filling server information
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(3332);
    servaddr.sin_addr.s_addr = inet_addr("172.16.223.10");

    
    const uint32_t events_per_packet = 128;
    const uint32_t time_per_packet = 10;

    const uint32_t _SPIF_OUTPUT_SET_LEN = 0x5ec40000;
    const uint32_t _SPIF_OUTPUT_SET_TICK = 0x5ec20000;
    const uint32_t _SPIF_OUTPUT_START = 0x5ec00000;

    const size_t ev_size_in_bytes = 4;
    const size_t spif_packet_size = events_per_packet * ev_size_in_bytes;
    const uint32_t spif_packet_time_us = time_per_packet;

    const size_t buff_size = 3 * sizeof(uint32_t);
    uint8_t bufout[buff_size];

    memcpy(bufout,
           &_SPIF_OUTPUT_SET_LEN + spif_packet_size, sizeof(uint32_t));
    memcpy(bufout + sizeof(uint32_t),
           &_SPIF_OUTPUT_SET_TICK + spif_packet_time_us, sizeof(uint32_t));
    memcpy(bufout + 2 * sizeof(uint32_t),
           &_SPIF_OUTPUT_START, sizeof(uint32_t));

    // // Send a message to the server
    sendto(sockfd, bufout, sizeof(bufout), 0, (const struct sockaddr *)&servaddr, sizeof(servaddr));

    // Wait for a response from the server

    char bufin[2048];
    socklen_t len = sizeof(cliaddr);
    int ev_count=0;

 
    
    std::cout << "Start"  << std::endl;  
    auto start_time = std::chrono::steady_clock::now();
    while (std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - start_time).count() < 10) {
        
        int n = recvfrom(sockfd, bufin, sizeof(bufin), 0, (struct sockaddr *)&cliaddr, &len);
        ev_count += n/ev_size_in_bytes;
    }

    std::cout << "End"  << std::endl; 
    std::cout << ev_count  << std::endl;  


    close(sockfd);
    return 0;
}