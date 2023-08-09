from fastapi import APIRouter

from app.api import v1

router = APIRouter(prefix="/api")
router.include_router(v1.router)
