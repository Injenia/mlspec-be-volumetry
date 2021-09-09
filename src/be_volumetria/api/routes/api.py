from fastapi import APIRouter

from be_volumetria.api.routes import healthz
from be_volumetria.api.routes.analysis import volumetry

router = APIRouter()

router.include_router(healthz.router, tags=["healthz"], prefix="/healthz")
router.include_router(volumetry.router, tags=["analysis"], prefix="/analysis")
