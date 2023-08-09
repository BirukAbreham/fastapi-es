import logging

from fastapi import FastAPI

from app import api
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.elasticsearch import close_es_connection, connect_to_es

# Setup logging configuration
setup_logging()

logger = logging.getLogger(__name__)

tags_metadata = [{"name": "ES API", "description": "Test ES endpoints"}]

app = FastAPI(
    debug=settings.DEBUG,
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json",
    docs_url=f"/api/{settings.API_VERSION}/docs",
    redoc_url=f"/api/{settings.API_VERSION}/redoc",
    openapi_tags=tags_metadata,
)

# Add the api routes
app.include_router(api.router)


@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting up")
    await connect_to_es()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Clean up before shutting down the server")
    await close_es_connection()
    logger.info("Application shutting down")
