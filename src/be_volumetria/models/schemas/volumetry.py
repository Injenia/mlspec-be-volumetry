from enum import Enum

from pydantic import BaseModel, Field


class Volume(str, Enum):
    type_1700 = '1700'
    type_2400 = '2400'
    type_3200 = '3200'
    type_sconosciuto = 'unknown'


class VolumetryResult(BaseModel):
    modelVersion: int = Field(..., example=1, description="Version of the ML model used for the inference")
    correlationId: str = Field(..., example="2009-10-31T01:48:52Z", description="_correlationId_ provided in input")
    volume: Volume = Field(..., example=Volume.type_2400, description="Volume type")