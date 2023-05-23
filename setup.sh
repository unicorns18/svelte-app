#!/bin/bash

# update system pkgs
echo "Updating system packages"
sudo apt-get update -y && sudo apt-get upgrade -y 2>/dev/null
echo "System packages updated successfully"

# install python pip
echo "Installing Python pip"
sudo apt install python3-pip -y 2>/dev/null
echo "Python pip installed successfully"

# install mongodb (for storing search history)
echo "Installing MongoDB"
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add - 2>/dev/null
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list 2>/dev/null
sudo apt update 2>/dev/null
sudo apt install mongodb-org -y 2>/dev/null
echo "MongoDB installed successfully"

# start mongodb
echo "Starting MongoDB"
sudo systemctl start mongod 2>/dev/null
echo "MongoDB started successfully"

# install python packages
echo "Installing python packages"
pip3 install -r requirements.txt 2>/dev/null echo "Python packages installed successfully"
echo "Python packages installed successfully"

# install nodejs
echo "Installing NodeJS"
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash - >/dev/null
sudo apt install -y nodejs >/dev/null
echo "NodeJS installed successfully"

# create mongodb db and collection
echo "Creating MongoDB database and collection"
mongo <<EOF 2>/dev/null
use search_history_db
db.createCollection('search_history')
EOF
echo "MongoDB database and collection created successfully"

# install npm
echo "Installing npm"
sudo apt install npm -y 2>/dev/null
echo "npm installed successfully"

# install npm dependencies
echo "Installing npm dependencies"
npm install 2>/dev/null
echo "npm dependencies installed successfully"