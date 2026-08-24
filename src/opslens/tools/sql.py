from typing import Any

from langchain_core.tools import tool
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from opslens.database import engine


def execute_read_only_query(query: str) -> list[dict[str, Any]]:
    normalized_query = query.strip()

    if not normalized_query.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")

    with engine.connect() as connection:
        result = connection.execute(text(normalized_query))
        rows = result.mappings().all()

    return [dict(row) for row in rows]


@tool
def run_sql_query(query: str) -> list[dict[str, Any]] | str:
    """
    Execute a read-only SELECT query against the OpsLens application database.

    Do not use this tool for MLflow data or MLflow tables.
    """

    try:
        return execute_read_only_query(query)

    except DBAPIError as error:
        return f"SQL_ERROR: {error.orig}"

    except (ValueError, RuntimeError) as error:
        return f"SQL_ERROR: {error}"
