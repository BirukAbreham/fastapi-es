from fastapi import APIRouter

from app.api.v1.endpoints import es_api
from app.core.config import settings

router = APIRouter(prefix=f"/{settings.API_VERSION}")

router.include_router(es_api.router, prefix="/es_api", tags=["ES API"])
