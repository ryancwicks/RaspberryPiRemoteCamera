"""
A set of classes for reading from a camera asynchronously and then capturing the images with a separate class.
"""
from PIL import Image
import numpy as np
import zmq
import time
import multiprocessing
from picamera import PiCamera
from picamera.array import PiRGBArray

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


# ZMQ settings
CAMERA_ZMQ_INTERFACE = "ipc://tmp/camera"
CAMERA_HIGH_WATER_MARK = 4


class CameraServer(multiprocessing.Process):
    """
    Class that reads from the camera in a separate process
    """

    def __init__(self, resolution="full-4:3"):
        super().__init__()
        self._camera = PiCamera()
        if resolution not in resolutions.keys():
            raise RuntimeError("Invalid Resolution Selected")
        self._camera.resolution = resolutions[resolution]
        self._camera.awb_gains = AWB_GAINS
        self._camera.framerate = FRAMERATE
        time.sleep(1)

        self._raw_capture = PiRGBArray(
            self._camera, size=resolutions[resolution])
        self.frame = None

        self._stop_capture = True

        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.set_hwm(CAMERA_HIGH_WATER_MARK)
        self._socket.bind(CAMERA_ZMQ_INTERFACE)

    @property
    def exposure(self):
        """
        Return the exposure time in ms
        """
        return self.camera.shutter_speed / 1E3

    @exposure.setter
    def exposure(self, exposure):
        """
        Set the exposure value (in ms)
        """
        if exposure == 0:
            self.camera.exposure_mode = "auto"
        else:
            self.camera.exposure_mode = "off"
        self.camera.shutter_speed = int(exposure*1E3)

    def start(self):
        """
        Start the capture
        """
        self._stop_capture = False

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
        self.camera.close()

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

    def _capture_continuous(self):
        """
        Capture images continuously from the camera.
        """
        while (True):
            if not self.stop_capture:
                stream = io.BytesIO()
                for frame in self._camera.capture_continuous(stream, format="jpeg", use_video_port=True):
                    frame.seek(0)
                    img = np.asarray(Image.open(frame))
                    CameraServer._send_array(self._socket, img)
                    self.raw_capture.truncate(0)
                    if self.stop_capture:
                        break
                    stream.seek(0)
            else:
                time.sleep(1)

    def run(self):
        """
        Run the process
        """
        self.stop_capture = False
        self._capture_continuous

    def stop(self):
        self.stop_capture = True


class CameraReader():
    """
    This class reads images published by the camera.
    """

    def __init__(self):
        """
        Initialize the zmq socket communication.
        """
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.SUB)
        self._socket.set_hwm(CAMERA_HIGH_WATER_MARK)
        self._socket.connect(CAMERA_INTERFACE)
        # subscribe to all sensors.
        self._socket.setsockopt(zmq.SUBSCRIBE, b"")

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
    def array_to_image(input_array: np.ndarray)->Image:
        """
        Turn an image array into a PILLOW image.
        """
        return Image.fromarray(input_array.astype('uint8'), 'RGB')

    def capture(self)->np.ndarray:
        """
        Return a 3 channel np.array (RGB)
        """
        output = CameraReader._recv_array(self._socket)
        return output
