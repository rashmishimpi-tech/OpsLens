from typing import Any

from langchain_core.tools import tool
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from opslens.data_sources import mlflow_engine
from opslens.tools.sql_validator import validate_mlflow_sql


def execute_mlflow_query(
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
    if mlflow_engine is None:
        raise RuntimeError("MLflow database is not configured")

    normalized_query = query.strip()

    if parameters:
        validate_mlflow_sql(normalized_query)
        executable_query = normalized_query
    else:
        executable_query = validate_mlflow_sql(normalized_query)

    with mlflow_engine.connect() as connection:
        try:
            connection.execute(
                text(f"EXPLAIN {executable_query}"),
                parameters or {},
            )

            result = connection.execute(text(executable_query), parameters or {})
            rows = result.mappings().all()

        except DBAPIError as error:
            original_error = error.orig

            raise ValueError(
                f"SQL validation failed: {original_error}"
            ) from error

    return [dict(row) for row in rows]

@tool
def run_mlflow_query(query: str) -> list[dict[str, Any]] | str:
    """Execute a guarded read-only SQL query against the MLflow metadata database.

    Use this tool for MLflow experiments, runs, metrics, params, tags,
    and latest_metrics."""
    try:
        return execute_mlflow_query(query)
    except (ValueError, RuntimeError) as error:
        return f"SQL_ERROR: {error}"


    