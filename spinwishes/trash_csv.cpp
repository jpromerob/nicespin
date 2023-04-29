#include <fstream>
#include <iostream>
#include <vector>
#include <sstream>

using namespace std;

int main(int argc, char* argv[])
{
    // Check that a filename was provided as an argument
    if (argc != 2) {
        cout << "Usage: " << argv[0] << " <filename>" << endl;
        return 1;
    }

    // Open the CSV file

    char* csv_file = argv[1];

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


    printf("Total lines in csv file: %d\n", line_counter);
    
    
    int my_Data[line_counter][2];
    int idx = 0;
    for (auto& row : data)
    {
        my_Data[idx][0] = row[0];
        my_Data[idx][1] = row[1];
        idx++;
    }


    for (int i=0; i<line_counter; i++){
        printf("(%d, %d)\n", my_Data[i][0], my_Data[i][1]);
    }


    return 0;
}