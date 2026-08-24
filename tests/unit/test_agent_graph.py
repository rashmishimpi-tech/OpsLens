from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from opslens.agent.graph import build_graph


def test_graph_returns_model_response_without_tool_call() -> None:
    mock_bound_model = MagicMock()
    mock_bound_model.invoke.return_value = AIMessage(
        content="Model latency is the time required to produce a response."
    )

    mock_model = MagicMock()
    mock_model.bind_tools.return_value = mock_bound_model

    with patch("opslens.agent.graph.get_model", return_value=mock_model):
        graph = build_graph()

        result = graph.invoke(
            {
                "messages": [
                    HumanMessage(content="What is model latency?"),
                ],
                "sql_retries": 0,
            }
        )

    messages = result["messages"]

    assert len(messages) == 2
    assert isinstance(messages[0], HumanMessage)
    assert isinstance(messages[1], AIMessage)
    assert messages[1].content == (
        "Model latency is the time required to produce a response."
    )

    mock_model.bind_tools.assert_called_once()
    mock_bound_model.invoke.assert_called_once()


def test_graph_executes_tool_and_returns_final_response() -> None:
    first_ai_message = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "run_sql_query",
                "args": {"query": "SELECT 1 AS value"},
                "id": "tool-call-1",
                "type": "tool_call",
            }
        ],
    )

    final_ai_message = AIMessage(
        content="The SQL query returned the value 1."
    )

    mock_bound_model = MagicMock()
    mock_bound_model.invoke.side_effect = [
        first_ai_message,
        final_ai_message,
    ]

    mock_model = MagicMock()
    mock_model.bind_tools.return_value = mock_bound_model

    with (
        patch("opslens.agent.graph.get_model", return_value=mock_model),
        patch(
            "opslens.tools.sql.execute_read_only_query",
            return_value=[{"value": 1}],
        ),
    ):
        graph = build_graph()

        result = graph.invoke(
            {
                "messages": [
                    HumanMessage(
                        content="Use SQL to run SELECT 1 AS value."
                    ),
                ],
                "sql_retries": 0,
            }
        )

    messages = result["messages"]

    assert len(messages) == 4

    assert isinstance(messages[0], HumanMessage)
    assert isinstance(messages[1], AIMessage)
    assert isinstance(messages[2], ToolMessage)
    assert isinstance(messages[3], AIMessage)

    assert messages[2].content == '[{"value": 1}]'
    assert messages[3].content == "The SQL query returned the value 1."

    assert mock_bound_model.invoke.call_count == 2