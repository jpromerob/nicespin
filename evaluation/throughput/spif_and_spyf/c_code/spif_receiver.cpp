#include <iostream>
#include <string.h>
#include <chrono>
#include <thread>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstdlib>
#include <ctime>
#include <cstring>
#include <sys/select.h>
#include <sys/types.h> 

using namespace std;

int main(int argc, char* argv[]) {

       if (argc != 4) {
              cerr << "Usage: " << argv[0] << "<ip-address> <ev_per_packet> <duration>" << endl;
              return 1;
       }

       int duration = atoi(argv[3]);
       // printf("Waiting for %d seconds\n", duration);

       int sockfd;
       struct sockaddr_in servaddr, cliaddr;

       // Creating socket file descriptor
       sockfd = socket(AF_INET, SOCK_DGRAM, 0);

       memset(&servaddr, 0, sizeof(servaddr));
       memset(&cliaddr, 0, sizeof(cliaddr));

       // Filling server information
       servaddr.sin_family = AF_INET;
       servaddr.sin_port = htons(3332);
       servaddr.sin_addr.s_addr = inet_addr(argv[1]);


       const uint32_t events_per_packet = atoi(argv[2]);
       const uint32_t time_per_packet = 10;

       const uint32_t _SPIF_OUTPUT_SET_LEN = 0x5ec40000;
       const uint32_t _SPIF_OUTPUT_SET_TICK = 0x5ec20000;
       const uint32_t _SPIF_OUTPUT_START = 0x5ec00000;

       const size_t ev_size_in_bytes = 4;
       const size_t spif_packet_size = events_per_packet * ev_size_in_bytes;
       const uint32_t spif_packet_time_us = time_per_packet;

       uint8_t bufout[3 * sizeof(uint32_t)];

       memcpy(bufout,
              &_SPIF_OUTPUT_SET_LEN + spif_packet_size, sizeof(uint32_t));
       memcpy(bufout + sizeof(uint32_t),
              &_SPIF_OUTPUT_SET_TICK + spif_packet_time_us, sizeof(uint32_t));
       memcpy(bufout + 2 * sizeof(uint32_t),
              &_SPIF_OUTPUT_START, sizeof(uint32_t));

       // // Send a message to the server
       sendto(sockfd, bufout, sizeof(bufout), 0, (const struct sockaddr *)&servaddr, sizeof(servaddr));

       // Wait for a response from the server

       char bufin[40*spif_packet_size];
       socklen_t len = sizeof(cliaddr);
       int pack_count=0;

       struct timeval read_timeout;
       read_timeout.tv_sec = 1;
       read_timeout.tv_usec = 0;
       setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &read_timeout, sizeof read_timeout);

       // std::cout << "Start"  << std::endl;  
       auto startTime = std::chrono::high_resolution_clock::now();
       auto endTime = startTime + std::chrono::seconds(duration);
       while (std::chrono::high_resolution_clock::now() < endTime) {
       // while (std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - start_time).count() < 10) {
              
              int n = recvfrom(sockfd, bufin, sizeof(bufin), 0, (struct sockaddr *)&cliaddr, &len);
              pack_count += max(n,0);
              // printf("... %d\n", pack_count);
       }

       // std::cout << "End"  << std::endl; 
       // std::cout << pack_count/ev_size_in_bytes  << std::endl;  
       std::cout << pack_count/ev_size_in_bytes  << std::endl;  


       close(sockfd);
       return 0;
}