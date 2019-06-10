#!/bin/bash 
rm -rf temp/
mkdir temp/
cp install_server.sh temp/
cp Dockerfile temp/
cp setup.py temp/
cp README.md temp/
cp LICENSE temp/
cp -r remote_camera temp/
#rsync -av --exclude='__pycache__' remote_camera temp/
cp -r remote_camera temp/
rm -rf temp/remote_camera/__pycache__
python -m zipfile -c pi_remote_camera.zip temp/*
rm -rf temp/
