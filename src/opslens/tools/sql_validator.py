import sqlglot
from sqlglot import exp

MLFLOW_ALLOWED_TABLES = {
    "experiments",
    "runs",
    "latest_metrics",
    "params",
    "tags",
    "metrics",
}

MAX_QUERY_LIMIT = 50

def validate_mlflow_sql(query: str) -> str:
    expression = sqlglot.parse_one(
        query,
        dialect="postgres"
    )

    if not isinstance(expression, exp.Select):
        raise ValueError("Only Select queries allowed")

    tables = {
        table.name
        for table in expression.find_all(exp.Table)
    }

    disallowed_tables = tables - MLFLOW_ALLOWED_TABLES

    if disallowed_tables:
        names = ", ".join(sorted(disallowed_tables))
        raise ValueError(f"Disallowed table: {names}")

    limit = expression.args.get("limit")

    if limit is None:
        expression = expression.limit(MAX_QUERY_LIMIT)
    else:
        limit_expression = limit.expression

        if isinstance(limit_expression, exp.Literal):
            requested_limit = int(limit_expression.this)

            if requested_limit > MAX_QUERY_LIMIT:
                expression = expression.limit(MAX_QUERY_LIMIT)

    return expression.sql(dialect="postgres")

    