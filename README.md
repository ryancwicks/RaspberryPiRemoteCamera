# RaspberryPiRemoteCamera
Containerized application for capturing still images from a remote Raspberry Pi.

# Setting up Image on the Raspberry Pi

Based on instructions found here:
https://www.thepolyglotdeveloper.com/2016/09/deploying-docker-containers-raspberry-pi-device/

Additionally, run

```bash
sudo raspi-config
```

Enable the camera, ssh, and set up the system to boot into the command line. Also set up any networking, as appropriate.


## Setting up Docker on the Raspberry Pi:

Install docker (and give the pi user access, assuming you are using the default username): 

```bash
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi
sudo systemctl enable docker
```