#include <arpa/inet.h>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <fstream>
#include <iostream>
#include <netinet/in.h>
#include <sstream>
#include <sys/socket.h>
#include <thread>
#include <unistd.h>
#include <vector>


using namespace std;

const uint16_t UDP_max_bytesize = 1024;
const uint16_t ev_size = 4; // 4 bytes


int send_request(char* argv[], int port, int ev_per_sec) {
    
    char* ip_address = argv[2];

    // create a UDP socket
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        std::cerr << "Error creating socket\n";
        return 1;
    }

    // set up the destination address
    struct sockaddr_in destaddr;
    std::memset(&destaddr, 0, sizeof(destaddr));
    destaddr.sin_family = AF_INET;
    destaddr.sin_addr.s_addr = inet_addr(ip_address); // IP address
    destaddr.sin_port = htons(port); // port number

    // send the message
    char message[10];
    std::sprintf(message, "%d", ev_per_sec);


    int n = sendto(sockfd, message, std::strlen(message), 0, (struct sockaddr*)&destaddr, sizeof(destaddr));
    if (n < 0) {
        std::cerr << "Error sending request message\n";
        return 1;
    }

    int res[6];
    memset(&res, 0, sizeof(res));
    // printf("Waiting for responses ... \n");
    recv(sockfd, &res, sizeof(res), 0);

    printf("%d,%d,%d,%d,%d,%d,%d\n", ev_per_sec, res[0], res[1], res[2], res[3], res[4], res[5]);


    std::ofstream file("my_data.csv", std::ios::app);
    file << ev_per_sec << "," << res[0] << "," << res[1]  << "," << res[3]  << "," << res[4] << std::endl;
    file.close();

    close(sockfd);

    return 0;
}

void thread_function(char* argv[], int (*coordinates)[2], int line_counter, int (*evs_sent), int idx) {
    
    
    //argv[0] << " <csv_fn> <ip-address> <port> <width> <t> <duration> <ev_per_pack> <nb_threads>
    
    int offset = idx; //std::rand() % 32767;

    char* spif_ip = argv[2];
    int port = atoi(argv[3]);
    int width = atoi(argv[4]);
    int sleeper = atoi(argv[5]);
    int duration = atoi(argv[6]);
    int ev_per_pack = atoi(argv[7]);
    
    /*****************************************************/
    /*                   Setup Socket                    */
    /*****************************************************/
    struct sockaddr_in udp_addr;
    memset(&udp_addr, 0, sizeof(udp_addr));
    udp_addr.sin_family = AF_INET;
    udp_addr.sin_port = htons(port);
    inet_pton(AF_INET, spif_ip, &udp_addr.sin_addr);

    int udp_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (udp_fd < 0) {
        cerr << "Error: Could not create socket." << endl;
    }


    /*****************************************************/
    /*                 Send events (loop)                */
    /*****************************************************/
    uint16_t message_sz = min(ev_per_pack, UDP_max_bytesize/ev_size);
    uint32_t message[message_sz]; // declare array


    auto start_t = std::chrono::steady_clock::now();

    int current_line = offset;
    int total_ev_sent = 0;

    while(true) {
        auto current_t = std::chrono::steady_clock::now();
        if(std::chrono::duration_cast<std::chrono::seconds>(current_t - start_t).count() > duration){
            break;
        }
        
        
        // assign values to elements using a for loop
        for (int i = 0; i < message_sz; i++) {
            
            uint16_t x = (uint16_t) (coordinates[current_line][0]);
            uint16_t y = (uint16_t) (coordinates[current_line][1]);
            // printf("(%d, %d)\n", x, y);
            uint32_t n = x+y*width;
            message[i] = n; // assign value to element i 
            if(current_line < line_counter-1){
                current_line++;
            } else {
                current_line = 0;
            }
        }

        // std::cout << "hello" << std::endl;
        if (sendto(udp_fd, &message, sizeof(message), 0, (struct sockaddr*)&udp_addr, sizeof(udp_addr)) < 0) {
            cerr << "Error: Failed to send data." << endl;
        }
        total_ev_sent += message_sz;
        
        if(sleeper>0){
            std::this_thread::sleep_for(std::chrono::microseconds(sleeper));
        }


    }
    // printf("Total events sent: %d\n", total_ev_sent);
    evs_sent[idx] = total_ev_sent;

    close(udp_fd);


}

int main(int argc, char* argv[]) {


    srand(time(NULL)); // seed the random number generator with the current time

    if (argc != 9) {
        cerr << "Usage: " << argv[0] << " <csv_fn> <ip-address> <port> <width> <t> <duration> <ev_per_pack> <nb_threads>" << endl;
        return 1;
    }

    int nb_threads = atoi(argv[8]);

    
    std::srand(std::time(nullptr));

    
    char* csv_file = argv[1];
    
    int evs_sent[64];
    std::memset(evs_sent, 0, sizeof(evs_sent));

    /*****************************************************/
    /*                   Load CSV file                   */
    /*****************************************************/
    ifstream infile(csv_file);
    vector<vector<int>> data;
    string line;
    int line_counter = 0;
    while (getline(infile, line))
    {
        stringstream ss(line);
        vector<int> values;
        string value;
        while (getline(ss, value, ','))
        {
            values.push_back(stoi(value));
        }
        data.push_back(values);
        line_counter++;
    }


    // printf("Total lines in csv file: %d\n", line_counter);
    
    int coordinates[32768][2];
    int idx = 0;
    for (auto& row : data)
    {
        coordinates[idx][0] = row[0];
        coordinates[idx][1] = row[1];
        idx++;
    }

    std::vector<std::thread> threads;
    for (int i = 0; i < nb_threads; ++i) {
        threads.emplace_back(thread_function, argv, coordinates, line_counter, evs_sent, i);
    }

    // Wait for all threads to finish
    for (auto& thread : threads) {
        thread.join();
    }

    std::this_thread::sleep_for(std::chrono::seconds(1));

    int total_ev_count = 0;
    for(int i=0; i<nb_threads; i++){
        total_ev_count += evs_sent[i];
    }

    send_request(argv, 4000, total_ev_count);
    return 0;
}