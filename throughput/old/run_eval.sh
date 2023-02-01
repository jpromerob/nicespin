#!/bin/bash

# run_eval.sh <SIZE> <FIRST_W> <NB_POINTS> <BOARD>

SIZE=$1
FIRST_W=$2
NB_POINTS=$3
BOARD=$4


for (( c=0; c<$NB_POINTS; c++ ))
do
    w=$(( $c * 4 + $FIRST_W ))
	echo "Simulations with w=$w"

    # SPIF
    # echo "python3 ~/nicespin/evaluation/evalsim.py -x $SIZE -y $SIZE -n 0.6 -b $BOARD -w $w"
    python3 ~/nicespin/evaluation/evalsim.py -x $SIZE -y $SIZE -n 4 -b $BOARD -w $w
    sleep 5

    # ENET
    # echo "python3 ~/nicespin/evaluation/evalsim.py -x $SIZE -y $SIZE -n 0.6 -b $BOARD -w $w -s"
    python3 ~/nicespin/evaluation/evalsim.py -x $SIZE -y $SIZE -n 4 -b $BOARD -w $w -s
    sleep 5
done
