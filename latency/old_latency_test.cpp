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
#include <bitset>
#include <cmath>
#include <fstream>


using namespace std;

const uint16_t ev_size = 4; // 4 bytes

const uint32_t P_SHIFT = 15;
const uint32_t Y_SHIFT = 0;
const uint32_t X_SHIFT = 16;
const uint32_t NO_TIMESTAMP = 0x80000000;

int main(int argc, char* argv[]) {

    if (argc != 4) {
            cerr << "Usage: " << argv[0] << "<ip-address> <ev_per_packet> <sleeper>" << endl;
            return 1;
    }

    int sleeper = atoi(argv[3]);

    int sockfd;
    struct sockaddr_in spif_in_addr, spif_out_addr, cliaddr;

    // Creating socket file descriptor
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);

    memset(&spif_out_addr, 0, sizeof(spif_out_addr));
    memset(&spif_in_addr, 0, sizeof(spif_in_addr));
    memset(&cliaddr, 0, sizeof(cliaddr));

    // Filling server information
    spif_out_addr.sin_family = AF_INET;
    spif_out_addr.sin_port = htons(3332);
    spif_out_addr.sin_addr.s_addr = inet_addr(argv[1]);


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
    sendto(sockfd, bufout, sizeof(bufout), 0, (const struct sockaddr *)&spif_out_addr, sizeof(spif_out_addr));



    spif_in_addr.sin_family = AF_INET;
    spif_in_addr.sin_port = htons(3333);
    spif_in_addr.sin_addr.s_addr = inet_addr(argv[1]);

    int message_sz = events_per_packet;
    int width = 640;
    int height = 480;
    uint32_t message[message_sz]; // declare array
    socklen_t len = sizeof(cliaddr);
    char bufin[20*spif_packet_size];

    int nb_pack_sent = 0;
    int nb_pack_recv = 0;
    uint16_t x_in;
    uint16_t y_in;
    uint16_t x_out;
    uint16_t y_out;



    int sz_array = 10000;
    float my_array[10000] = {};
    int array_idx = 0;
    while(array_idx < sz_array){

        
        for (int i = 0; i < message_sz; i++) {
            
            x_in = (uint16_t) (rand() % width);
            y_in = (uint16_t) (rand() % height);
            uint32_t n = (NO_TIMESTAMP + (1 << P_SHIFT) + (y_in << Y_SHIFT) + (x_in << X_SHIFT));
            message[i] = n; // assign value to element i 


        }
        
        auto start_time = std::chrono::high_resolution_clock::now();

        // std::cout << "hello" << std::endl;
        if (sendto(sockfd, &message, sizeof(message), 0, (struct sockaddr*)&spif_in_addr, sizeof(spif_in_addr)) < 0) {
            cerr << "Error: Failed to send data." << endl;
            return 1;
        }
        nb_pack_sent += 1;


        int n = recvfrom(sockfd, bufin, sizeof(bufin), 0, (struct sockaddr *)&cliaddr, &len);



        auto end_time = std::chrono::high_resolution_clock::now();
        auto elapsed_time = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);
        

        uint32_t* received_data = (uint32_t*) bufin;
        y_out = (received_data[0] >> 10) & 0x03FF;
        x_out = (received_data[0] >> 0) & 0x03FF;


        if ((x_out == x_in) && (y_out == y_in)){
            my_array[array_idx] = float(elapsed_time.count())/1000000.0;
            std::cout << "dt:\t" << elapsed_time.count() << " [us] : " <<  x_out << "," << y_out << std::endl;
        }

        nb_pack_recv += max(n,0);       

        std::this_thread::sleep_for(std::chrono::microseconds(sleeper));
        array_idx++;

    }

    int n = sizeof(my_array) / sizeof(my_array[0]); 
    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        sum += my_array[i];
    }
    double avg = sum / n;

    // Calculate the standard deviation
    double variance = 0.0;
    for (int i = 0; i < n; i++) {
        variance += pow(my_array[i] - avg, 2);
    }
    double stdev = sqrt(variance / n);

    // Print the results
    std::cout << "Total Evs: " << n << std::endl;
    std::cout << "Average: " << avg << std::endl;
    std::cout << "Standard deviation: " << stdev << std::endl;



    // Create a file stream
    std::ofstream myfile("spif_latency.csv");

    // Write the array to the file
    for (int i = 0; i < n; i++) {
        myfile << my_array[i] << ",0,0,0,0\n";
    }
    myfile << std::endl;

    // Close the file stream
    myfile.close();

    close(sockfd);
    return 0;
}


