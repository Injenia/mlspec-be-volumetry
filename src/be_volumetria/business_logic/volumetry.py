from be_volumetria.business_logic.ml import VolumetriaInferenceEnsambleHub
from be_volumetria.core.config import CROP_COORDS_SX, CROP_COORDS_DX
from fastapi.param_functions import File
from loguru import logger
from typing import Tuple
from PIL import Image

import json
import io


class ModelNotLoadedError(Exception):
    pass

volumetria_model = VolumetriaInferenceEnsambleHub()

###############################################################################


def crop_image_bytes(bytes_in: bytes, ymin: float, xmin: float,
                     ymax: float, xmax: float, format: str) -> bytes:
    """
    Crops an image given as a bytestring, returning the bytestring of the cropped image

    :param bytes_in: Image bytes
    :param ymin,xmin,ymax,xmax: Crop relative position, values must be in [0,1]
    :param format: Image format of output bytestring. Must be compatible with PIL image formats
    
    :returns: Image bytes of cropped image
    """
    logger.debug("Entering crop_image_bytes")
    buffer = io.BytesIO()
    buffer.write(bytes_in)
    buffer.seek(0)
    img = Image.open(buffer)
    width, height = img.size
    crop = img.crop((
        xmin * width,     # left
        ymin * height,    # upper
        xmax * width,     # right
        ymax * height     # lower
    ))
    output = io.BytesIO()
    crop.save(output, format=format)
    output.seek(0)
    bytes_out = output.read()
    return bytes_out

def crop_image(image_file: File, crop_coords: dict) -> bytes:
    im_bytes = image_file.read()
    crop_bytes = crop_image_bytes(im_bytes, format="JPEG", **crop_coords)
    return crop_bytes

def crop_images(image_sx: File, image_dx: File) -> Tuple[bytes, bytes]:
    logger.debug("Entering crop_images")
    crop_sx_bytes = crop_image(image_sx, CROP_COORDS_SX)
    crop_dx_bytes = crop_image(image_dx, CROP_COORDS_DX)
    return crop_sx_bytes, crop_dx_bytes


def calc_volume(image_sx: File, image_dx: File) -> str:
    """
    Main function to evaluate dumpster volume. First, it crops the images provided then proceeds
    to call the ml model for prediction

    :param image_sx: file-like object of the left image
    :param image_dx: file-like object of the right image

    :returns: the predicted class
    """
    logger.debug("Entering calc_volume")
    crop_bytes_sx, crop_bytes_dx = crop_images(image_sx, image_dx)

    inference_results = volumetria_model.predict(crop_bytes_sx, crop_bytes_dx)
    volume = inference_results["label"]
    return volume.decode("utf-8")
