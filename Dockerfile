FROM arm32v7/python

COPY setup.py /opt
COPY README.md /opt
COPY remote_camera /opt/remote_camera

RUN pip install /opt/
RUN pip install picamera

#Need to set REMOTE_CAMERA_SECRET_KEY environment variable.

CMD ["run_server]

