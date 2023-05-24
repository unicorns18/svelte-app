#!/bin/bash

# update system pkgs
echo "Updating system packages"
sudo apt-get update -y && sudo apt-get upgrade -y 2>/dev/null
echo "System packages updated successfully"

# install nodejs
echo "Installing NodeJS"
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash - >/dev/null
sudo apt install -y nodejs >/dev/null
echo "NodeJS installed successfully"

# install npm
echo "Installing npm"
sudo apt install npm -y 2>/dev/null
echo "npm installed successfully"

# install npm dependencies
echo "Installing npm dependencies"
npm install 2>/dev/null
echo "npm dependencies installed successfully"