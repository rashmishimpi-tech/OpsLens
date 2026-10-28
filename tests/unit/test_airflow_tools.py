
from unittest.mock import patch

from opslens.tools.airflow import (
    get_failed_dag_runs,
    get_failed_task_instances,
)

def test_get_failed_task_instances() -> None:
    dag_id = "opslens_demo"
    run_id = "manual__test_run"

    expected_result = [
        {
            "dag_id": dag_id,
            "run_id": run_id,
            "task_id": "train",
            "state": "failed",
            "try_number": 1,
        }
    ]

    with patch(
        "opslens.tools.airflow.execute_airflow_query",
        return_value=expected_result,
    ) as mock_query:
        result = get_failed_task_instances.invoke(
            {
                "dag_id": dag_id,
                "run_id": run_id,
            }
        )

    assert result == expected_result

    mock_query.assert_called_once()

    query = mock_query.call_args.args[0]
    parameters = mock_query.call_args.args[1]

    assert "FROM task_instance" in query
    assert "state = 'failed'" in query

    assert parameters == {
        "dag_id": dag_id,
        "run_id": run_id,
    }



def test_get_failed_dag_runs() -> None:
    dag_id = "opslens_demo"

    expected_result = [
        {
            "dag_id": dag_id,
            "run_id": "manual__test_run",
            "state": "failed",
        }
    ]

    with patch(
        "opslens.tools.airflow.execute_airflow_query",
        return_value=expected_result,
    ) as mock_query:
        result = get_failed_dag_runs.invoke(
            {"dag_id": dag_id}
        )

    assert result == expected_result

    mock_query.assert_called_once()

    query = mock_query.call_args.args[0]
    parameters = mock_query.call_args.args[1]

    assert "FROM dag_run" in query
    assert "state = 'failed'" in query
    assert "ORDER BY start_date DESC" in query

    assert parameters == {"dag_id": dag_id}
