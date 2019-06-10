"""
A set of classes for reading from a camera asynchronously and then capturing the images with a separate class.
"""
from sys import platform
from PIL import Image
import numpy as np
import zmq
import time
import multiprocessing
import io
from importlib import util
picam_spec = util.find_spec("picamera")
picam_found = picam_spec is not None
if picam_found:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
else:
    import pkg_resources
    test_image_filepath = pkg_resources.resource_filename(
        __name__, 'static/test_pattern.png')


# Values for the V2 picamera
resolutions = {
    'full-4:3': (3280, 2464),
    'partial-4:3': (1640, 1232),
    'small-4:3': (640, 480),
    'large-16:9': (1920, 1080),
    'medium-16:9': (1640, 922),
    'small-16:9': (1280, 720),
}
AWB_GAINS = 1.6
FRAMERATE = 10

if platform == "linux" or platform == "linux2":
    CAMERA_ZMQ_DATA_INTERFACE = "ipc:///tmp/cameradata"
    CAMERA_ZMQ_DATA_READER_INTERFACE = "ipc:///tmp/cameradata"
    CAMERA_ZMQ_CONTROL_INTERFACE = "ipc:///tmp/cameracontrol"
    CAMERA_ZMQ_CONTROL_READER_INTERFACE = "ipc:///tmp/cameracontrol"
else:
    CAMERA_ZMQ_DATA_INTERFACE = "tcp://*:5555"
    CAMERA_ZMQ_DATA_READER_INTERFACE = "tcp://localhost:5555"
    CAMERA_ZMQ_CONTROL_INTERFACE = "tcp://*:5556"
    CAMERA_ZMQ_CONTROL_READER_INTERFACE = "tcp://localhost:5556"

CAMERA_HIGH_WATER_MARK = 1


class CameraServer(multiprocessing.Process):
    """
    Class that reads from the camera in a separate process
    """

    def __init__(self, resolution="full-4:3"):
        super().__init__()
        self._stop_capture = False
        self._break_capture = False
        self._resolution = resolutions[resolution]

    @property
    def exposure(self):
        """
        Return the exposure time in ms
        """
        if picam_found:
            return self._camera.shutter_speed / 1E3
        else:
            return self._exposure

    @exposure.setter
    def exposure(self, exposure):
        """
        Set the exposure value (in ms)
        """
        if picam_found:
            if exposure == 0:
                self._camera.exposure_mode = "auto"
            else:
                self._camera.exposure_mode = "off"
            self._camera.shutter_speed = int(exposure*1E3)
        else:
            self._exposure = exposure

    @property
    def resolution(self):
        """
        Set the resolution
        """
        return self._resolution

    @resolution.setter
    def resolution(self, resolution):
        """
        Set the resolution to scale the image to.
        """
        if not isinstance(resolution, tuple):
            raise TypeError("Resolution must be a tuple")
        self._resolution = resolution

    def __enter__(self):
        """
        Context manager enter
        """
        self.start()
        return self

    def close(self):
        """
        Called to clean up camera context.
        """
        self.stop()
        if picam_found:
            self._camera.close()

    def __exit__(self, *args):
        """
        Context manager exit
        """
        self.close()

    @staticmethod
    def _send_array(socket, A, flags=0, copy=True, track=False):
        """
        send a numpy array with metadata
        """
        md = dict(
            dtype=str(A.dtype),
            shape=A.shape,
        )
        socket.send_json(md, flags | zmq.SNDMORE)
        return socket.send(A, flags, copy=copy, track=track)

    def _handle_control_message(self, message):
        """
        Handle requests from the camera reader (in another process)
        """
        response = {"success": True}
        if "request" not in message:
            response["success"] = False
            response["message"] = "Invalid message received by camera."
        if message["request"] == "get_exposure":
            response["exposure"] = self.exposure
        elif message["request"] == "set_exposure":
            try:
                self.exposure = int(message["exposure"])
                response["exposure"] = self.exposure
            except KeyError:
                response["success"] = False
                response["message"] = "Exposure not sent with exposure request."
        elif message["request"] == "set_exposure":
            try:
                self.resolution = (message["width"], message["height"])
                # Cause the system to reset the resolution.
                self._break_capture = True
            except:
                response["success"] = False
                response["message"] = "Could not set resolution"
        elif message['request'] == "get_exposure":
            response['width'] = self.resolution[0]
            response['height'] = self.resolution[1]
        elif message["request"] == "stop_capture":
            self.stop()
        elif message["request"] == "start_capture":
            self.start()

        self._socket_control.send_json(response)

    def _poll_control(self):
        """
        """
        try:
            control_message = self._socket_control.recv_json(
                flags=zmq.NOBLOCK)
            self._handle_control_message(control_message)
        except zmq.Again:
            pass

    def _capture_continuous(self):
        """
        Capture images continuously from the camera.
        """
        try:
            while (not self._stop_capture):

                if not self._stop_capture:
                    if picam_found:
                        stream = io.BytesIO()
                        self._raw_capture = PiRGBArray(
                            self._camera, size=self.resolution)
                        for frame in self._camera.capture_continuous(stream, format="jpeg", use_video_port=True, resize=self.resolution):
                            frame.seek(0)
                            img = np.asarray(Image.open(frame))
                            CameraServer._send_array(self._socket_data, img)
                            self._raw_capture.truncate(0)
                            if self._stop_capture or self._break_capture:
                                self._break_capture = False
                                break
                            stream.seek(0)
                            self._poll_control()
                    else:
                        CameraServer._send_array(self._socket_data, self.img)
                        time.sleep(1.0 / FRAMERATE)
                        self.poll_control()
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            pass

    def run(self):
        """
        Run the process
        """
        self._stop_capture = False

        # needs to be setup up once inside new process, doesn't work otherwise.
        self._context = zmq.Context()
        self._socket_data = self._context.socket(zmq.PUB)
        self._socket_data.set_hwm(CAMERA_HIGH_WATER_MARK)
        self._socket_data.bind(CAMERA_ZMQ_DATA_INTERFACE)

        self._socket_control = self._context.socket(zmq.REP)
        self._socket_control.bind(CAMERA_ZMQ_CONTROL_INTERFACE)

        if picam_found:
            self._camera = PiCamera()
            self._camera.resolution = self.resolution
            self._camera.awb_gains = AWB_GAINS
            self._camera.framerate = FRAMERATE
        time.sleep(1)

        if picam_found:
            self._raw_capture = PiRGBArray(
                self._camera, size=self.resolution)
            self.frame = None
        else:
            self._exposure = 5
            self.img = np.asarray(Image.open(
                test_image_filepath).convert('RGB'))

        self._capture_continuous()

    def stop(self):
        self._stop_capture = True


class CameraReader():
    """
    This class reads images published by the camera.
    """

    def __init__(self):
        """
        Initialize the zmq socket communication.
        """
        self._context = zmq.Context()
        # set up data subscriber
        self._socket_data = self._context.socket(zmq.SUB)
        self._socket_data.set_hwm(CAMERA_HIGH_WATER_MARK)
        self._socket_data.connect(CAMERA_ZMQ_DATA_READER_INTERFACE)
        # subscribe to all sensors.
        self._socket_data.setsockopt(zmq.SUBSCRIBE, b"")

        # set up the control interface
        self._socket_control = self._context.socket(zmq.REQ)
        self._socket_control.connect(CAMERA_ZMQ_CONTROL_READER_INTERFACE)

    @staticmethod
    def _recv_array(socket, flags=0, copy=True, track=False):
        """
        recv a numpy array
        """
        md = socket.recv_json(flags=flags)
        msg = socket.recv(flags=flags, copy=copy, track=track)
        A = np.frombuffer(msg, dtype=md['dtype'])
        try:
            A = A.reshape(md['shape'])
            return A
        except:
            return None

    @staticmethod
    def array_to_image(input_array: np.ndarray) -> Image:
        """
        Turn an image array into a PILLOW image.
        """
        return Image.fromarray(input_array.astype('uint8'), 'RGB')

    def capture(self) -> np.ndarray:
        """
        Return a 3 channel np.array (RGB)
        """
        output = CameraReader._recv_array(self._socket_data)
        return output

    @property
    def exposure(self):
        """
        Return the exposure time in ms
        """
        message = {"request": "get_exposure"}
        self._socket_control.send_json(message)
        response = self._socket_control.recv_json()
        try:
            if not response["success"]:
                raise RuntimeError(response["message"])
        except KeyError as err:
            print("Invalid response from camera server - {}".format(err))

        return response["exposure"]

    @exposure.setter
    def exposure(self, exposure):
        """
        Set the exposure value (in ms)
        """
        message = {"request": "set_exposure",
                   "exposure": exposure}
        self._socket_control.send_json(message)
        response = self._socket_control.recv_json()
        try:
            if not response["success"]:
                raise RuntimeError(response["message"])
        except KeyError as err:
            print("Invalid response from camera server - {}".format(err))

    @property
    def resolution(self):
        """
        Return the current resolution
        """
        message = {"request": "get_resolution"}
        self._socket_control.send_json(message)
        response = self._socket_control.recv_json()
        try:
            if not response["success"]:
                raise RuntimeError(response["message"])
        except KeyError as err:
            print("Invalid response from camera server - {}".format(err))

        return (response["width"], response["height"])

    def set_resolution(self, width, height):
        """
        Set the image resolution
        """
        message = {"request": "set_resolution",
                   "width": width,
                   "height": height}
        self._socket_control.send_json(message)
        response = self._socket_control.recv_json()
        try:
            if not response["success"]:
                raise RuntimeError(response["message"])
        except KeyError as err:
            print("Invalid response from camera server - {}".format(err))

    def stop_capture(self):
        """
        stop the capture
        """
        message = {"request": "stop_capture"}
        self._socket_control.send_json(message)
        response = self._socket_control.recv_json()
        try:
            if not response["success"]:
                raise RuntimeError(response["message"])
        except KeyError as err:
            print("Invalid response from camera server - {}".format(err))

    def start_capture(self):
        """
        start the capture
        """
        message = {"request": "start_capture"}
        self._socket_control.send_json(message)
        response = self._socket_control.recv_json()
        try:
            if not response["success"]:
                raise RuntimeError(response["message"])
        except KeyError as err:
            print("Invalid response from camera server - {}".format(err))
