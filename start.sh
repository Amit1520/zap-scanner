#!/bin/bash

# Download ZAP if not already there
if [ ! -d "zap" ]; then
  echo "Downloading ZAP..."
  mkdir zap
  curl -L -o zap/ZAP_Linux.tar.gz https://github.com/zaproxy/zaproxy/releases/download/v2.16.1/ZAP_2.16.1_Linux.tar.gz
  tar -xzf zap/ZAP_Linux.tar.gz -C zap --strip-components=1
fi

# Start ZAP in daemon mode
./zap/zap.sh -daemon -config api.key=$ZAP_API_KEY &

# Wait for ZAP to start
sleep 15

# Start your Flask app
python app.py
