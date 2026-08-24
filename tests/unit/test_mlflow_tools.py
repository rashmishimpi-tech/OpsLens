from unittest.mock import patch

from opslens.tools.mlflow import get_run_metrics


def test_get_run_metrics_uses_run_name() -> None:
    expected = [
        {
            "key": "accuracy",
            "value": 0.91,
            "timestamp": 123456,
            "step": 0,
        }
    ]

    with patch(
        "opslens.tools.mlflow.execute_mlflow_query",
        return_value=expected,
    ) as mock_execute:
        result = get_run_metrics.invoke(
            {"run_name": "baseline-training"}
        )

    assert result == expected

    mock_execute.assert_called_once()

    query, parameters = mock_execute.call_args.args

    assert ":run_name" in query
    assert parameters == {
        "run_name": "baseline-training"
    }