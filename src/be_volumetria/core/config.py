import json
import logging
import sys
import os
from typing import Optional

from loguru import logger
from starlette.config import Config

# Static settings
API_PREFIX = "/api"
VERSION = "0.2.0"
PROJECT_NAME = "be-volumetria"

config = Config(".env")

# Logging configuration
DEBUG: bool = config("DEBUG", cast=bool, default=False)
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOG_HOST: str = config("LOG_HOST", cast=str, default=None)
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])

# Back-end specific configurations
VOLUMETRIA_MODEL_SX: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ml_models', 'model_sx')  # Base model - mandatory
VOLUMETRIA_MODEL_DX: Optional[str] = None  # optional, if omitted VOLUMETRIA_MODEL_SX will be used

# Load & set ML model info
model_info_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ml_models', 'model_info.json')
model_info = json.load(open(model_info_path))
UNKNOWN_CLASS_THRESHOLD: float = float(model_info["model_sx"]["unknown_class_threshold"])
CROP_COORDS_SX = model_info["model_sx"]["crop_coords_sx"]
CROP_COORDS_DX = model_info["model_sx"]["crop_coords_dx"]

MSG_SOURCE = "injenia.be-volumetria"
