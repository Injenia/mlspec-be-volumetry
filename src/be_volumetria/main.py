from collections import Callable

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.exceptions import HTTPException

from be_volumetria.api.errors.http_error import http_error_handler
from be_volumetria.api.errors.validation_error import http422_error_handler
from be_volumetria.api.routes.api import router as api_router
from be_volumetria.core.config import API_PREFIX
from be_volumetria.core.config import DEBUG
from be_volumetria.core.config import LOG_HOST
from be_volumetria.core.config import MSG_SOURCE
from be_volumetria.core.config import PROJECT_NAME
from be_volumetria.core.config import VERSION


def set_log_host():
    def endpoint_builder(level: str) -> Callable:
        async def endpoint_sink(msg: str):
            endpoint_level = level.lower()
            async with httpx.AsyncClient(base_url=LOG_HOST) as client:
                body = {"message": msg, "source": MSG_SOURCE}
                await client.post(f"/api/v1/log/{endpoint_level}", json=body)

        return endpoint_sink

    logger.add(endpoint_builder("WARNING"), level="WARNING", enqueue=True)
    logger.add(endpoint_builder("ERROR"), level="ERROR", enqueue=True)
    logger.add(endpoint_builder("INFORMATION"), level="INFO", enqueue=True)
    if DEBUG:
        logger.add(endpoint_builder("DEBUG"), level="DEBUG", enqueue=True)


def get_application() -> FastAPI:
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)
    application.include_router(api_router, prefix=API_PREFIX)

    if LOG_HOST:  # Send the logs to endpoint if the URL is provided
        logger.info(f"Log host provided, logs will be redirected to `{LOG_HOST}`")
        set_log_host()

    return application


app = get_application()

if __name__ == "__main__":  # for debugging purpose
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
