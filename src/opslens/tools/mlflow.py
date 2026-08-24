from typing import Any

from langchain_core.tools import tool

from opslens.tools.mlflow_sql import execute_mlflow_query


@tool
def get_run_metrics(run_name: str) -> list[dict[str, Any]]:
    """
    Get the latest metrics for an MLflow run by its run name
    Use this only when the user identifies one specific run by name,
    such as "baseline-training".

    Do not use this tool for:
    - filtering runs by metric values
    - comparing multiple runs
    - finding runs where a metric is above or below a threshold
    - questions where no specific run name is provided

    Use run_mlflow_query for those analytical questions
    """

    query = """
    SELECT m.key, m.value, m.timestamp, m.step
    FROM latest_metrics AS m
    JOIN runs AS r
        ON m.run_uuid = r.run_uuid
    WHERE r.name =:run_name
    ORDER BY m.key
    """

    return execute_mlflow_query(
        query,
        {"run_name": run_name}
    )

