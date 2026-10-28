
from typing import Any

from langchain_core.tools import tool
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from opslens.data_sources import airflow_engine
from opslens.tools.sql_validator import validate_airflow_sql


def execute_airflow_query(
    query: str,
    parameters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Execute validated SQL against Airflow metadata."""

    if airflow_engine is None:
        raise RuntimeError("Airflow database is not configured")

    executable_query = validate_airflow_sql(query)

    try:
        with airflow_engine.connect() as connection:
            with connection.begin():
                # PostgreSQL enforces read-only access.
                connection.execute(
                    text("SET TRANSACTION READ ONLY")
                )

                # Timeout applies to this transaction only.
                connection.execute(
                    text("SET LOCAL statement_timeout = '5s'")
                )

                # Check whether PostgreSQL can plan the query.
                connection.execute(
                    text(f"EXPLAIN {executable_query}"),
                    parameters or {},
                )

                result = connection.execute(
                    text(executable_query),
                    parameters or {},
                )

                rows = result.mappings().all()

        return [dict(row) for row in rows]

    except DBAPIError as error:
        raise ValueError(
            f"Airflow SQL execution failed: {error.orig}"
        ) from error


@tool
def run_airflow_query(query: str) -> list[dict[str, Any]] | str:
    """Execute a guarded SELECT query against Airflow metadata.

    Use for DAG runs, task instances, DAG status, and import errors.
    Do not use for MLflow or OpsLens application data.
    """

    try:
        return execute_airflow_query(query)

    except (ValueError, RuntimeError) as error:
        return f"SQL_ERROR: {error}"
