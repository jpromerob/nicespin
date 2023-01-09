#!/bin/bash

# run_eval.sh <BOARD> <FIRST_W> <NB_PTS>

BOARD=$1
FIRST_W=$2
NB_PTS=$3


for (( c=0; c<$NB_PTS; c++ ))
do
    b=$(( $c * 4 + $FIRST_W ))
	echo "Simulations with w=$b"

    # SPIF
    python3 ~/nicespin/evaluation/fastersim.py -x 40 -y 40 -b $BOARD -w $b 
    sleep 5

    # ENET
    python3 ~/nicespin/evaluation/fastersim.py -x 40 -y 40 -b $BOARD -w $b -s
    sleep 5
done
