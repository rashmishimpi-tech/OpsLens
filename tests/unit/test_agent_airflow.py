
from opslens.agent.graph import build_graph, tools


def test_airflow_tools_registered() -> None:
    tool_names = {tool.name for tool in tools}

    assert "get_failed_dag_runs" in tool_names
    assert "get_failed_task_instances" in tool_names


def test_agent_graph_compiles() -> None:
    graph = build_graph()

    assert graph is not None
    assert "agent" in graph.nodes
    assert "tools" in graph.nodes
    assert "retry" in graph.nodes
    assert "empty_result" in graph.nodes
