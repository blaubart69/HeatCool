#!/bin/bash
while true
do
	./logging_write.sh
	dt=$(date '+%d/%m/%Y %H:%M:%S');
	echo "$dt w"
	sleep 1
done
