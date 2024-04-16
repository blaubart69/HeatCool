#!/bin/sh

TOKEN="Tx-tv3oJiXnQf48LNc_4L99qeD3d3Hz3NySh6AjXeaCwzr4pizoTXYx1eeG1o2k83qzorpFBEzO_S9YEQwK2Og=="

  ./logging_query.sh            \
| ./logging_transform2influx.sh \
| influx write -o beeorg -b spidata --format=lp --token="$TOKEN"

