#!/bin/sh

# to not conflict with an other cron job running in the exact same second
sleep 30

tempww="$(/usr/local/bin/htquery 'Temp. Brauchwasser')"

data="ww,sensor_id=temp_brauchwasser temperature=$tempww"
echo $data

curl --request POST \
	"http://pi.local:8086/api/v2/write?org=beeorg&bucket=wp&precision=s" \
  --header "Authorization: Token Tx-tv3oJiXnQf48LNc_4L99qeD3d3Hz3NySh6AjXeaCwzr4pizoTXYx1eeG1o2k83qzorpFBEzO_S9YEQwK2Og==" \
  --header "Content-Type: text/plain; charset=utf-8" \
  --header "Accept: application/json" \
  --data-binary "$data"

