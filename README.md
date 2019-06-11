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
rsync -avz ./ pi@<pi ip address>:remote_camera/ --exclude 'venv' --exclude '__pycache__' --exclude '*.egg-info' --exclude ".*"
```

# Issues

This is not a secure device. The application runs uwsgi as the http server directly and as root. All the data is sent in the clear. Don't so something silly like connect it to a public network.

Images captured by the camera are stored at full resolution, and then down sampled to the requested image size on the server using the CPU. Framerate through the web interface is about 0.75 Hz. This could be sped up with lower resolutions for the preview being captured or resized on the GPU. 

The camera starts in auto exposure mode, but if you change the exposure, you remain in fixed exposure mode until you restart the device.


