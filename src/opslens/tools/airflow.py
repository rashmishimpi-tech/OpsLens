
from typing import Any

from langchain_core.tools import tool

from opslens.tools.airflow_sql import execute_airflow_query


@tool
def get_failed_dag_runs(dag_id: str) -> list[dict[str, Any]] | str:
    """Retrieve recent failed Airflow DAG runs for a specific DAG.

    Use this tool when investigating Airflow DAG failures.
    The dag_id must be the exact Airflow DAG identifier.
    """

    query = """
        SELECT
            dag_id,
            run_id,
            state,
            start_date,
            end_date
        FROM dag_run
        WHERE dag_id = :dag_id
          AND state = 'failed'
        ORDER BY start_date DESC
        LIMIT 20
    """

    try:
        return execute_airflow_query(
            query,
            {"dag_id": dag_id},
        )

    except (ValueError, RuntimeError) as error:
        return f"SQL_ERROR: {error}"



@tool
def get_failed_task_instances(
    dag_id: str,
    run_id: str,
) -> list[dict[str, Any]] | str:
    """Retrieve failed Airflow task instances for a specific DAG run.

    Use this tool to identify which tasks failed after finding
    a failed DAG run.

    Both dag_id and run_id must be exact Airflow identifiers.
    """
    query = """
        SELECT
            dag_id,
            run_id,
            task_id,
            state,
            try_number,
            start_date,
            end_date,
            duration
        FROM task_instance
        WHERE dag_id = :dag_id
          AND run_id = :run_id
          AND state = 'failed'
        ORDER BY start_date DESC
        LIMIT 20
    """

    try:
        return execute_airflow_query(
            query,
            {
                "dag_id": dag_id,
                "run_id": run_id,
            },
        )
    except (ValueError, RuntimeError) as error:
        return f"SQL_ERROR: {error}"
