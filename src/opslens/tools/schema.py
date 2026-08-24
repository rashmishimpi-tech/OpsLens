from sqlalchemy import inspect

from opslens.database import engine


def get_database_schema() -> str:
    inspector = inspect(engine)

    table_names = [
        table_name
        for table_name in inspector.get_table_names()
        if table_name != "alembic_version"
    ]

    if not table_names:
        return "No application tables are currently available"

    lines: list[str] = []

    for table_name in table_names:
        lines.append(f"Table: {table_name}")

        columns = inspector.get_columns(table_name)
        for col in columns:
            column_name = col['name']
            column_type = col["type"]

            lines.append(f"- {column_name} : {column_type}")

    return "\n".join(lines)