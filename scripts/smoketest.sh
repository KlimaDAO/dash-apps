#!/bin/bash

FAILING=0

for a in src/apps/tco2_dashboard/app.py; do
  module="${a////.}"
  nohup python -m ${module%.py} &
  DASH_PID=$!
  sleep 30
  RESP_CODE=$(curl --head --location --write-out %{http_code} --silent --output response.txt http://127.0.0.1:8050/)
  echo $RESP_CODE
  kill `lsof -w -n -i tcp:8050 | awk '$2!="PID" {print $2;}'`
  if [ "$RESP_CODE" != "200" ];
  then
    echo "$a FAILED! ($RESP_CODE)"
    echo "--------------"
    echo "Server Logs:"
    cat nohup.out
    echo "--------------"
    echo "UI response:"
    cat response.txt
    FAILING=1
  else
    echo "$a OK ($RESP_CODE)"
  fi
done

if [ $FAILING -eq 1 ];
then
  echo "ERROR"
  exit 1
else
  echo "SUCCESS"
  exit 0
fi
