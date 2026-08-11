from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from opslens.database import check_database_connection

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness() -> dict[str, str]:
    try:
        check_database_connection()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        ) from exc

    return {"status": "ready"}
