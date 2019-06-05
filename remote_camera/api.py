"""
This part of the flask app responds to api requests
"""
from Flask import Blueprint, jsonify, request
from remote_camera.camera import CameraReader
from io import BytesIO
import base64

bp = Blueprint("api", __name__, "/api/v1.0/")


@bp.route("/get_image", defaults={'width': None, 'height': None})
@bp.route("/get_image/<int:width>,<int:height>")
def get_image(width, height):
    """
    Get an image from the camera in a json response in base64 encoding. If width and height are provided, return a scaled image.
    """
    response = {"success": True}
    cam = CameraReader()

    image_size = None
    if width is not None and height is not None:
        image_size = (width, height)
    try:
        image_array = cam.capture()
        image = cam.array_to_image(image_array)
    except:
        response["success"] = False
        response["message"] = "Failed to capture an image."

    response["image"] = get_base_64_image(image, image_size)
    return jsonify(response)


@bp.route("/exposure", defaults={'exposure'=None})
@bp.route("/exposure/<int:exposure>")
def exposure(exposure):
    """
    Setter or getter for the camera exposure value.
    """
    response = {"success": True}
    cam = CameraReader()
    if not exposure:
        try:
            response["exposure"] = cam.exposure
        except:
            response["success"] = False
            response["message"] = "Failed to read exposure from camera."
    else:
        try:
            cam.exposure = exposure
            response["exposure"] = cam.exposure
        except:
            response["success"] = False
            response["message"] = "Failed to set exposure from camera."

    return jsonify(response)


@bp.route("/start_capture")
def start():
    """
    Start camera capture.
    """
    cam = CameraReader()
    response = {"success": True}
    try:
        cam.stop_capture()
    except:
        response["success"] = False
        response["message"] = "Failed to start camera capture."
    return jsonify(response)


@bp.route("/stop_capture")
def stop():
    """
    Stop camera capture.
    """
    cam = CameraReader()
    response = {"success": True}
    try:
        cam.stop_capture()
    except:
        response["success"] = False
        response["message"] = "Failed to stop camera capture."
    return jsonify(response)


def get_base_64_image(image, size=None):
    """
    Return the image resized with base64 encoding, ready to be sent with json.
    """
    if size:
        new_image = image.resize(size)
    else:
        new_image = image
    output_stream = BytesIO()
    new_image.save(output_stream, format='jpeg')
    output_stream.seek(0)

    return base64.b64encode(output_stream)
