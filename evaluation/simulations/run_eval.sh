#!/bin/bash

START=0
END=15

cd  ~/nicespin/evaluation/simulations
for (( c=$START; c<=$END; c++ ))
do
    b=$(( $c * 4 + 56 ))
	echo "Simulations with w=$b"
    python3 ~/nicespin/evaluation/evalsim.py -x 40 -y 40 -w $b 
    rig-power 172.16.223.0
    sleep 5
    python3 ~/nicespin/evaluation/evalsim.py -x 40 -y 40 -w $b -s
    rig-power 172.16.223.0
    sleep 5
done