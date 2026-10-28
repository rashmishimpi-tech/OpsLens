import sqlglot
from sqlglot import exp

MLFLOW_ALLOWED_TABLES = frozenset({
    "experiments",
    "runs",
    "latest_metrics",
    "params",
    "tags",
    "metrics",
})

AIRFLOW_ALLOWED_TABLES = frozenset({
    "dag",
    "dag_run",
    "task_instance",
    "import_error",
})

MAX_QUERY_LIMIT = 50


def _validate_sql(
        query: str,
        allowed_tables: frozenset[str],
) -> str:
    statements = sqlglot.parse(query, dialect="postgres")

    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Only a single SQL statement is allowed")

    expression = statements[0]

    if not isinstance(expression, exp.Select):
        raise ValueError("Only Select queries allowed")

    # Reject potentially unsafe nested operations.
    forbidden_types = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Create,
        exp.Alter,
        exp.Into,
        exp.Command,
    )

    if any(isinstance(node, forbidden_types) for node in expression.walk()):
        raise ValueError("Only Select queries allowed")

    # Reject SQL function calls by default
    if any(isinstance(node, exp.Func) and not isinstance(node, exp.Connector) for node in expression.walk()):
        raise ValueError("SQL function calls are not allowed")

    tables = {
        table.name
        for table in expression.find_all(exp.Table)
    }

    if not tables:
        raise ValueError("Query must reference at least one table")

    disallowed_tables = tables - allowed_tables

    if disallowed_tables:
        names = ", ".join(sorted(disallowed_tables))
        raise ValueError(f"Disallowed table: {names}")

    limit = expression.args.get("limit")

    if limit is None:
        expression = expression.limit(MAX_QUERY_LIMIT)
    else:
        limit_expression =  limit.expression

        if not isinstance(limit_expression, exp.Literal):
            raise ValueError("Limit must be a literal integer")

        try:
            requested_limit = int(limit_expression.this)
        except (TypeError, ValueError) as error:
            raise ValueError("Limit must be an integer") from error

        if requested_limit < 0:
            raise ValueError("Limit must be a non-negative integer")

        if requested_limit > MAX_QUERY_LIMIT:
            expression = expression.limit(MAX_QUERY_LIMIT)

    return expression.sql()
    

def validate_mlflow_sql(query: str) -> str:
    return _validate_sql(query, MLFLOW_ALLOWED_TABLES)

def validate_airflow_sql(query: str) -> str:
    return _validate_sql(query, AIRFLOW_ALLOWED_TABLES)