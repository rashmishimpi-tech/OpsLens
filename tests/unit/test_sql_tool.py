from unittest.mock import MagicMock, patch

import pytest

from opslens.tools.sql import execute_read_only_query


def test_execute_read_only_query_returns_rows() -> None:
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = [
        {"value" : 1},
    ]

    mock_connection = MagicMock()
    mock_connection.execute.return_value = mock_result

    mock_context_manager = MagicMock()
    mock_context_manager.__enter__.return_value = mock_connection

    with patch(
        "opslens.tools.sql.engine.connect",
        return_value = mock_context_manager,
    ):
        result = execute_read_only_query("SELECT 1 AS value")

    assert result == [{"value": 1}]
    mock_connection.execute.assert_called_once()

def test_execute_read_only_query_rejects_non_select() -> None:
    with pytest.raises(ValueError, match="Only SELECT queries are allowed."):
        execute_read_only_query("DELETE FROM model_runs")


    