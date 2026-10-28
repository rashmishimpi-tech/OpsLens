
import pytest

from opslens.tools.sql_validator import validate_airflow_sql


def test_valid_airflow_select() -> None:
    query = "SELECT dag_id, state FROM dag_run"

    validated = validate_airflow_sql(query)

    assert "FROM dag_run" in validated
    assert "LIMIT 50" in validated


def test_reject_mlflow_table() -> None:
    query = "SELECT * FROM runs"

    with pytest.raises(ValueError, match="Disallowed table"):
        validate_airflow_sql(query)


def test_reject_delete_query() -> None:
    query = "DELETE FROM dag_run"

    with pytest.raises(ValueError, match="Only Select queries allowed"):
        validate_airflow_sql(query)


def test_reject_multiple_statements() -> None:
    query = "SELECT * FROM dag_run; DELETE FROM dag_run"

    with pytest.raises(ValueError, match="Only a single SQL statement"):
        validate_airflow_sql(query)


def test_enforce_maximum_limit() -> None:
    query = "SELECT * FROM dag_run LIMIT 1000"

    validated = validate_airflow_sql(query)

    assert "LIMIT 50" in validated
    assert "LIMIT 1000" not in validated


def test_reject_sql_functions() -> None:
    query = "SELECT COUNT(*) FROM dag_run"

    with pytest.raises(ValueError, match="SQL function calls"):
        validate_airflow_sql(query)


def test_reject_missing_table() -> None:
    query = "SELECT 1"

    with pytest.raises(ValueError, match="must reference"):
        validate_airflow_sql(query)


def test_preserve_airflow_named_parameter() -> None:
    query = (
        "SELECT dag_id FROM dag_run "
        "WHERE dag_id = :dag_id LIMIT 20"
    )

    validated = validate_airflow_sql(query)

    assert ":dag_id" in validated
    assert "%(dag_id)s" not in validated


def test_preserve_different_parameter_names() -> None:
    query = (
        "SELECT dag_id, state FROM dag_run "
        "WHERE dag_id = :dag_id "
        "AND state = :run_state LIMIT 20"
    )

    validated = validate_airflow_sql(query)

    assert ":dag_id" in validated
    assert ":run_state" in validated
    assert "%(dag_id)s" not in validated
    assert "%(run_state)s" not in validated

def test_preserve_placeholder_like_string_literal() -> None:
    query = (
        "SELECT dag_id FROM dag_run "
        "WHERE dag_id = :dag_id "
        "AND state = '%(run_state)s' LIMIT 20"
    )

    validated = validate_airflow_sql(query)

    assert ":dag_id" in validated
    assert "'%(run_state)s'" in validated