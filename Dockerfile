FROM arm32v7/python

COPY setup.py /opt
COPY install_server.sh /opt
COPY remote_camera /opt

#Need to set REMOTE_CAMERA_SECRET_KEY environment variable.

RUN CHMOD 755 /opt/install_server.sh

CMD ["/opt/install_server.sh"]

