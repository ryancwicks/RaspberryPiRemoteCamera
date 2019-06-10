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


# Setting up the Raspberry Pi to run the site through nginx and uwsgi

Start by copying the site files over the to pi:

```bash
rsync -avz ./ pi@<pi ip address>:remote_camera/ --exclude 'venv' --exclude '__pycache__' --exclude '*.egg-info'
```

