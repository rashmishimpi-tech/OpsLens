
# Airflow Integration — Phase 4

## Overview

OpsLens integrates with Apache Airflow to investigate workflow
execution failures using Airflow metadata stored in PostgreSQL.

The integration is read-only. OpsLens does not schedule, trigger,
retry, or modify Airflow DAGs.

## Architecture

The components run in separate environments:

- Apache Airflow runs in Ubuntu WSL2.
- Airflow stores metadata in PostgreSQL running in Docker.
- OpsLens runs in its own Python environment.
- OpsLens accesses Airflow metadata through SQLAlchemy and psycopg.

The Airflow Python package is not required in the OpsLens
application environment.

## Database Separation

Three PostgreSQL databases serve distinct purposes:

| Database | Purpose |
|----------|---------|
| opslens | OpsLens application data |
| mlflow | MLflow tracking metadata |
| airflow | Airflow workflow metadata |

OpsLens uses the `AIRFLOW_DATABASE_URL` configuration setting
to connect to Airflow metadata.

Database credentials must be stored outside version control.

## Airflow Tools

### get_failed_dag_runs

Input:
- dag_id

Queries the `dag_run` table to retrieve recent failed
executions of the specified DAG.

Returns:
- dag_id
- run_id
- state
- start_date
- end_date

### get_failed_task_instances

Inputs:
- dag_id
- run_id

Queries the `task_instance` table to identify failed tasks
within a specific DAG execution.

Returns:
- dag_id
- run_id
- task_id
- state
- try_number
- start_date
- end_date
- duration

## SQL Safety

Airflow queries pass through a SQL validation layer.

Current safeguards include:

- SELECT-only statement validation
- Allowed-table restrictions
- SQL function restrictions
- Query result limits
- SQLAlchemy parameter binding
- Read-only transaction execution
- PostgreSQL statement timeout

A dedicated database account with SELECT-only permissions
is recommended for defense in depth.

These safeguards have not undergone a comprehensive
security audit and should not be treated as sufficient
for unrestricted production SQL generation.

## LangGraph Integration

Both Airflow tools are registered in the existing
LangGraph tool registry.

The agent is instructed to:

1. Identify the relevant DAG.
2. Retrieve failed DAG runs.
3. Select the appropriate run.
4. Retrieve failed task instances.
5. Explain findings using retrieved evidence.

Airflow and MLflow data are kept logically separate.

Cross-system correlations require supporting evidence.

## Validation

Completed:

- Airflow metadata database connectivity
- Failed DAG run retrieval
- Failed task instance retrieval
- SQL validation unit tests
- Airflow tool unit tests
- Agent tool-registration tests
- LangGraph graph compilation tests
- Full automated test suite: 27 passing

Pending:

- Live LLM-driven Airflow investigation
- Verification of the complete agent tool-call sequence
- Task exception and log retrieval
- Comprehensive security and production-readiness review

## Known Limitations

- Current tools identify failed DAG runs and tasks but do
  not retrieve task logs or exception messages.
- The live Qwen/Ollama investigation has not been verified.
- SQL validation supports a restricted query subset.
- Database access requires correct PostgreSQL permissions.
- Automated tests do not replace full end-to-end validation.

## Future Improvements

- Retrieve Airflow task logs and exception details.
- Improve agent investigation reliability.
- Add controlled integration and end-to-end tests.
- Expand observability across Airflow and MLflow.
- Review security, database permissions, and query limits.
