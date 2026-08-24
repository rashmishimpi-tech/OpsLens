from langchain_core.messages import ToolMessage

from opslens.agent.graph import (
    handle_empty_result,
    increment_sql_retries,
    route_after_tool,
)
from opslens.agent.state import AgentState


def test_sql_error_routes_to_retry() -> None:
    state: AgentState = {
        "messages": [
            ToolMessage(
                content="SQL_ERROR: column run_id does not exist",
                tool_call_id="test-call",
            )
        ],
        "sql_retries": 0,
    }

    result = route_after_tool(state)

    assert result == "retry"


def test_sql_error_stops_after_one_retry() -> None:
    state: AgentState = {
        "messages": [
            ToolMessage(
                content="SQL_ERROR: column run_id does not exist",
                tool_call_id="test-call",
            )
        ],
        "sql_retries": 1,
    }

    result = route_after_tool(state)

    assert result == "end"


def test_success_routes_back_to_agent() -> None:
    state: AgentState = {
        "messages": [
            ToolMessage(
                content='[{"run_uuid": "abc123"}]',
                tool_call_id="test-call",
            )
        ],
        "sql_retries": 0,
    }

    result = route_after_tool(state)

    assert result == "agent"


def test_increment_sql_retries() -> None:
    state: AgentState = {
        "messages": [],
        "sql_retries": 0,
    }

    result = increment_sql_retries(state)

    assert result["sql_retries"] == 1


def test_empty_sql_result_routes_to_empty_result() -> None:
    state: AgentState = {
        "messages": [
            ToolMessage(
                content="[]",
                tool_call_id="test-call",
            )
        ],
        "sql_retries": 0,
    }

    result = route_after_tool(state)

    assert result == "empty_result"


def test_handle_empty_result_returns_grounded_message() -> None:
    state: AgentState = {
        "messages": [],
        "sql_retries": 0,
    }

    result = handle_empty_result(state)

    messages = result["messages"]

    assert len(messages) == 1
    assert messages[0].content == "No matching data was found."