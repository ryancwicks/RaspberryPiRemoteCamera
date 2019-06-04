FROM arm32v7/python

COPY setup.py /opt
COPY install_server.sh
COPY remote_camera /opt

RUN CHMOD 755 /opt/install_server.sh

CMD ["/opt/install_server.sh"]

