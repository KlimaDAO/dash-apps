#!/bin/bash

FAILING=0

ENTRIES=(src/apps/api/app.py:/api/v1 src/apps/treasury/index.py:/)

for ENTRY in ${ENTRIES[@]}; do
  ITEMS=(`echo $ENTRY | tr ":" " "`)
  APP=${ITEMS[0]}
  SUBPATH=${ITEMS[1]}
  URL=http://127.0.0.1:8050$SUBPATH
  echo $APP : Starting
  module="${APP////.}"
  nohup python -m ${module%.py} > /tmp/nohup.out 2>&1 &
  DASH_PID=$!
  echo $APP : Launched with PID $DASH_PID
  sleep 30
  echo $APP : Pinging $URL
  RESP_CODE=$(curl --head --location --write-out %{http_code} --silent --output response.txt $URL)
  echo $APP : Response code: $RESP_CODE
  kill $DASH_PID
  # kill `lsof -w -n -i tcp:8050 | awk '$2!="PID" {print $2;}'` | head -n 1
  if [ "$RESP_CODE" != "200" ];
  then
    echo "$APP : FAILED! ($RESP_CODE)"
    echo "--------------"
    echo "UI response:"
    cat response.txt
    echo "--------------"
    echo "Server Logs:"
    cat /tmp/nohup.out
    FAILING=1
  else
    echo "$APP OK ($RESP_CODE)"
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
