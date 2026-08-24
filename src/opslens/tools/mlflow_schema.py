from sqlalchemy import inspect

from opslens.data_sources import mlflow_engine

MLFLOW_TABLES = {
    "experiments",
    "runs",
    "metrics",
    "params",
    "tags",
    "latest_metrics",
}

def get_mlflow_schema() -> str:
    if mlflow_engine is None:
        return "No Supported Mlflow tables are available"

    inspector = inspect(mlflow_engine)

    available_tables = set(inspector.get_table_names())
    table_names = sorted(MLFLOW_TABLES & available_tables)

    if not table_names:
        return "No Supported Mlflow tables are available"

    lines: list[str] = []

    for table_name in table_names:
        lines.append(f"Tables: {table_name}")

        for column in inspector.get_columns(table_name):
            lines.append(f" - {column["name"]} : {column["type"]}")

    return "\n".join(lines)

