from typing import List

from fastapi import APIRouter
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import UploadFile
from loguru import logger

from be_volumetria.business_logic.volumetry import calc_volume
from be_volumetria.models.schemas.volumetry import Volume
from be_volumetria.models.schemas.volumetry import VolumetryResult


def check_image_format(files: List[UploadFile]):
    supported_formats = ["image/jpeg"]

    for file in files:
        if file.content_type not in supported_formats:
            msg = f"File '{file.filename}' has the format '{file.content_type}' that is not supported."
            logger.warning(msg)
            raise HTTPException(status_code=415, detail=msg)


router = APIRouter()
api_description = """
Send three images from the vehicle cams and get the estimation of the dumpster type captured in the images, if any.\n
If no dumpster type is recognized, the result type is `unknown`.\n
Raise a `415` error if any of the images provided are not in jpeg format.
"""


# noinspection PyPep8Naming
@router.post("/volumetry",
             name="analysis:dumpster volumetry estimation",
             description=api_description,
             response_model=VolumetryResult)
async def centering(
        correlationId: str = Form(..., description="correlationId associated to the current centering analysis"),
        camLeft: UploadFile = File(..., description="Image to be analyzed from the _Left_ camera"),
        camCenter: UploadFile = File(..., description="Image to be analyzed from the _Center_ camera"),
        camRight: UploadFile = File(..., description="Image to be analyzed from the _Right_ camera"),
) -> VolumetryResult:
    logger.info(f"New volume request - "
                f"camLeft: `{camLeft.filename}`-{camLeft.content_type} | "
                f"camCenter: `{camCenter.filename}`-{camCenter.content_type} | "
                f"camRight: `{camRight.filename}`-{camRight.content_type} | "
                f"correlationId: `{correlationId}`")

    check_image_format([camLeft, camCenter, camRight])
    volume = calc_volume(camLeft.file, camRight.file)
    modelVersion = 1
    logger.info(f"Volume output - "
                f"modelVersion: `{modelVersion}` | "
                f"correlationId: `{correlationId}` | "
                f"volume: `{volume}`")

    return VolumetryResult(modelVersion=modelVersion,
                           correlationId=correlationId,
                           volume=Volume(volume))
