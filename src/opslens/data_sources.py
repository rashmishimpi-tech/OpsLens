from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from opslens.config import get_settings

settings = get_settings()

def create_optional_engine(database_url: str | None) -> Engine | None:
    if not database_url:
        return None

    return create_engine(
        database_url,
        pool_pre_ping=True
    )


mlflow_engine = create_optional_engine(settings.mlflow_database_url)
airflow_engine = create_optional_engine(settings.airflow_database_url)