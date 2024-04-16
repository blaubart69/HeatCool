#!/bin/sh
awk -F ' *\[MP,..\]: *' '{ gsub(" ","_",$1);  print "wp_logging "$1"="$2  }'
