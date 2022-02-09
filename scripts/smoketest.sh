#!/bin/bash

FAILING=0

for a in src/apps/*/app.py; do
  module="${a////.}"
  python -m ${module%.py} &
  DASH_PID=$!
  sleep 10
  RESP_CODE=$(curl --head --location --write-out %{http_code} --silent --output /dev/null http://127.0.0.1:8050/)
  echo $RESP_CODE
  kill `lsof -w -n -i tcp:8050 | awk '$2!="PID" {print $2;}'`
  if [ "$RESP_CODE" != "200" ];
  then
    echo "$a FAILED! ($RESP_CODE)"
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
