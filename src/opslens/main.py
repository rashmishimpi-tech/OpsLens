import logging

from fastapi import FastAPI

from opslens.api import router
from opslens.config import get_settings
from opslens.logging_config import configure_logging

configure_logging()

settings = get_settings()
logger = logging.getLogger("opslens")

app = FastAPI(
    title=settings.app_name,
    description="OpsLens API for managing operations and monitoring.",
    version=settings.app_version,
)

app.include_router(router)


@app.on_event("startup")
async def startup() -> None:
    logger.info(
        "Opslens API starting up",
        extra={
            "app_name": settings.app_name,
            "environment": settings.environment,
        },
    )


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "environment": settings.environment,
    }
