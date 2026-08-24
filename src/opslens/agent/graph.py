from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from opslens.agent.model import get_model
from opslens.agent.state import AgentState
from opslens.tools.mlflow import get_run_metrics
from opslens.tools.mlflow_schema import get_mlflow_schema
from opslens.tools.mlflow_sql import run_mlflow_query
from opslens.tools.sql import run_sql_query

tools = [
    get_run_metrics,
    run_sql_query,
    run_mlflow_query,
]

MAX_SQL_RETRIES = 1

def call_model(state: AgentState) -> dict[str, object]:
    model = get_model().bind_tools(tools)

    mlflow_schema = get_mlflow_schema()

    system_prompt = f"""
    You are OpsLens, an operational intelligence assistant.

    Your role is to help engineers investigate ML operational issues.

    Rules:
    - answer clearly and concisely
    - distinguish facts from assumptions
    - never invent operational data
    - use the MLflow SQL tool when MLflow data is required
    - only use tables and columns present in the provided schema
    - never claim database results unless they came from the MLflow SQL tool
    - if a tool returns no rows, say that no matching data was found
    - do not invent fallback values when a tool returns an empty result

    Important MLflow relationships:
    - runs.run_uuid is the primary identifier for a run
    - runs.name is the human-readable run name
    - metrics.run_uuid references runs.run_uuid
    - latest_metrics.run_uuid references runs.run_uuid
    - params.run_uuid references runs.run_uuid
    - tags.run_uuid references runs.run_uuid
    - if the user gives a run name, join through the runs table to find its run_uuid
    - do not compare latest_metrics.run_uuid directly to a run name
    - latest_metrics already contains the latest value for each metric key for a run
    - when the user asks for "metrics" in plural, return all matching latest_metrics rows;
    - do not use LIMIT 1 unless the user explicitly asks for one metric or one row
    - never infer that other data does not exist merely because the SQL query used LIMIT

    Column ownership rules:
    - runs.name exists only in runs
    - metrics contains run_uuid, key, value, timestamp, step, is_nan
    - latest_metrics contains run_uuid, key, value, timestamp, step, is_nan
    - params contains run_uuid, key, value
    - tags contains run_uuid, key, value
    - if the answer needs a run name together with metrics, params, or tags, JOIN that 
      table to runs using run_uuid

    Parameter vs metric rules:
    - hyperparameters and configuration values such as learning_rate, batch_size, 
      model_type belong in params
    - measured numeric outcomes such as accuracy, loss, latency_ms belong in 
      metrics/latest_metrics
    - when the user asks which runs used a parameter value, query params and join to
      runs using run_uuid

    MLflow database schema:

    {mlflow_schema}

    MLflow SQL examples:

    Question: Find the run named baseline-training.
    SQL:
    SELECT run_uuid, name, status, experiment_id
    FROM runs
    WHERE name = 'baseline-training'

    Question: Get the latest metrics for a run named baseline-training.
    SQL:
    SELECT m.key, m.value, m.timestamp, m.step
    FROM latest_metrics AS m
    JOIN runs AS r
        ON m.run_uuid = r.run_uuid
    WHERE r.name = 'baseline-training'
    ORDER BY m.key

    Question: Get the parameters for a run named baseline-training.
    SQL:
    SELECT p.key, p.value
    FROM params AS p
    JOIN runs AS r
        ON p.run_uuid = r.run_uuid
    WHERE r.name = 'baseline-training'
    ORDER BY p.key

    Question: Show failed MLflow runs.
    SQL:
    SELECT run_uuid, name, status, start_time, end_time
    FROM runs
    WHERE status = 'FAILED'
    ORDER BY start_time DESC

    Question: Which runs have accuracy greater than 0.90?
    SQL:
    SELECT r.run_uuid, r.name, m.value
    FROM runs AS r
    JOIN latest_metrics AS m
        ON r.run_uuid = m.run_uuid
    WHERE m.key = 'accuracy'
    AND m.value > 0.90

    Question: Which runs used learning_rate 0.01?
    SQL:
    SELECT r.run_uuid, r.name, p.value
    FROM runs AS r
    JOIN params AS p
        ON r.run_uuid = p.run_uuid
    WHERE p.key = 'learning_rate'
    AND p.value = '0.01'

    Use these examples only as patterns.
    Generate SQL dynamically based on the user's actual question.
    Do not assume the user is asking about baseline-training.

    Tool routing rules:
    - use run_mlflow_query for all MLflow experiments, runs, metrics, params, and tags
    - never query MLflow tables using run_sql_query
    - run_sql_query is only for the OpsLens application database
    - emit at most one tool call for the same SQL query in a single response

    Tool selection:
    - use get_run_metrics only when the user provides one specific MLflow
    run name and asks for that run's latest metrics
    - a metric name, comparison, threshold, or condition is never a run name
    - do not pass expressions such as "accuracy > 0.90" as run_name
    - questions that search, filter, compare, rank, or aggregate across runs
    must use run_mlflow_query
    - prefer get_run_metrics for the common case of retrieving all latest
    metrics for one explicitly named run
    - use run_mlflow_query for other MLflow analytical questions
    - use run_sql_query only for the OpsLens application database
    """
    response = model.invoke(
        [
            SystemMessage(content=system_prompt),
            *state["messages"]
        ]
    )

    return {
        "messages" : [response],
    }

def build_graph() -> CompiledStateGraph[AgentState]:
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("agent", call_model)
    graph_builder.add_node("tools", ToolNode(tools))
    graph_builder.add_node("retry", increment_sql_retries)
    graph_builder.add_node("empty_result", handle_empty_result)

    graph_builder.add_edge(START, "agent")
    graph_builder.add_conditional_edges(
        "agent",
        tools_condition
    )

    graph_builder.add_conditional_edges(
        "tools",
        route_after_tool,
        {
            "agent":"agent",
            "retry":"retry",
            "empty_result":"empty_result",
            "end": END,
        },
    )

    graph_builder.add_edge("retry", "agent")
    graph_builder.add_edge("empty_result", END)

    return graph_builder.compile()


def route_after_tool(state: AgentState) -> str:
    last_message = state["messages"][-1]

    content = str(last_message.content)

    if content.startswith("SQL_ERROR:"):
        if state["sql_retries"] >= MAX_SQL_RETRIES:
            return "end"

        return "retry"

    if content == "[]":
        return "empty_result"

    return "agent"


def increment_sql_retries(state: AgentState) -> dict[str, int]:
    return {
        "sql_retries": state["sql_retries"] + 1
    }

def handle_empty_result(state: AgentState) -> dict[str, list[AIMessage]]:
    return {
        "messages": [
            AIMessage(
                content="No matching data was found."
            )
        ]
    }

        
