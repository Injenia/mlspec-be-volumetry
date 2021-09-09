from datetime import datetime

from fastapi import APIRouter

from be_volumetria.models.schemas.healthz import HealthCheck

router = APIRouter()


@router.get("",
            response_model=HealthCheck,
            name="healthz:check",
            description="Return current timestamp in ISO-8601 format."
            )
async def healthz_check() -> HealthCheck:
    return HealthCheck(timestamp=datetime.now().isoformat())
