#!/bin/bash

# Install Java 17 (Ubuntu/Debian)
apt-get update
apt-get install -y openjdk-17-jre

# Export JAVA_HOME if needed
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# Download and run ZAP
echo "Downloading ZAP..."
wget https://github.com/zaproxy/zaproxy/releases/download/v2.14.0/ZAP_2.14.0_unix.sh -O zap.sh
chmod +x zap.sh
./zap.sh -cmd -daemon -port 8080 -config api.key="$ZAP_API_KEY" &

# Start your Flask app
python3 app.py
