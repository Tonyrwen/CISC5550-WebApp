#!/bin/bash

apt-get update -y
apt-get upgrade -y
apt-get install -y wget
apt-get install unzip
apt-get install -y python3-pip
pip3 install --upgrade flask
pip3 install flask-login
pip3 install flask-wtf
pip3 install WTForms 

# download the code
wget https://github.com/Tonyrwen/CISC5550-WebApp/archive/refs/heads/main.zip
unzip main.zip
cd CISC5550-WebApp-main
python3 todolist_api.py
