from flask import Flask
import time
from remote_camera.camera import CameraServer, CameraReader

camera_server = None

DEBUG = False


def get_camera():
    """
    get access to the global camera object.
    """
    global camera_server
    if camera_server == None:
        camera_server = CameraServer()
    return camera_server


def initialize():
    """
    Start the hardware
    """
    cam = get_camera()
    cam.start()


def create_app(test_config=None):
    """
    Create the flask application
    """
    application = Flask(__name__)
    # application.config.from_envvar(
    #    SECRET_KEY='REMOTE_CAMERA_SECRET_KEY'
    # )
    initialize()
    # allow time for the camera to start before first requests.
    time.sleep(1.5)
    from remote_camera import app
    from remote_camera import api

    application.register_blueprint(app.bp)
    application.register_blueprint(api.bp)

    return application


def main():
    """
    Main entry point for the program.
    """

    port = 5000
    app = create_app()
    app.run(host='0.0.0.0', port=port, debug=DEBUG, use_reloader=False)
