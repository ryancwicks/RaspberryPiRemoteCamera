#!/bin/bash

#sudo apt-get update
#sudo apt-get install python3-pip -y
#sudo apt-get install nginx -y
#python3 -m venv venv
#source venv/bin/activate
#pip install .

sudo chown www-data site_data

sudo cp uwsgi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start uwsgi.service
sudo systemctl enable uwsgi.service