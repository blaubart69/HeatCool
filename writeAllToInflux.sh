#!/bin/sh

sleep 20

TOKEN="Tx-tv3oJiXnQf48LNc_4L99qeD3d3Hz3NySh6AjXeaCwzr4pizoTXYx1eeG1o2k83qzorpFBEzO_S9YEQwK2Og=="

/usr/local/bin/htquery | awk -F ' *: *' '{ gsub(" ","_",$1);  print "wp "$1"="$2  }' >lp.txt
influx write -o beeorg -b spidata --format=lp -f ./lp.txt --token="$TOKEN"

