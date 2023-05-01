 #!/bin/bash

# First Argumeny: Check (1 or 0)
# Second Argument: ev/packet
# Third Argument: sleeper

./c_code/send_csv_events.exe 172.16.223.10:3333 coords_xy.csv 256 "$3" 1 "$2" "$1"
sleep 1
