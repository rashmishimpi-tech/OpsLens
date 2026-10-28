from sqlalchemy import inspect

from opslens.data_sources import airflow_engine

AIRFLOW_TABLES = frozenset({
    "dag",
    "dag_run",
    "task_instance",
    "import_error",
})

def get_airflow_schema() -> str:
    if airflow_engine is None:
        return "No supported Airflow tables are available"

    inspector = inspect(airflow_engine)

    available_tables = set(inspector.get_table_names())
    table_names = sorted(AIRFLOW_TABLES & available_tables)

    if not table_names:
        return "No supported Airflow tables are available"

    lines: list[str] = []

    for table_name in table_names:
        lines.append(f"Table: {table_name}")

        for columns in inspector.get_columns(table_name):
            lines.append(f"  Column: {columns['name']} ({columns['type']})")

    return "\n".join(lines)