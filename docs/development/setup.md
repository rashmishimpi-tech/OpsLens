# Development Setup

This document describes how to configure a local development environment for OpsLens.

## Prerequisites

Install the following tools before setting up the project:

- Python 3.12
- uv
- Docker Desktop
- Git

Verify the installations:

```powershell
python --version
uv --version
docker --version
docker compose version
git --version
```

OpsLens currently targets Python 3.12.

---

## Clone the Repository

Clone the repository and enter the project directory:

```powershell
git clone https://github.com/rashmishimpi-tech/OpsLens.git
cd OpsLens
```

Development work should be performed on feature branches rather than directly on `main`.

---

## Environment Configuration

OpsLens uses a local `.env` file for environment-specific configuration.

Create it from the committed example:

```powershell
Copy-Item .env.example .env
```

Update the values in `.env` if required for your local environment.

The `.env` file must never be committed to Git. `.env.example` documents the configuration expected by the project without containing real secrets.

---

## Python Environment and Dependencies

OpsLens uses `uv` for Python environment and dependency management.

Install the project dependencies:

```powershell
uv sync
```

`uv` will synchronize the environment using:

- `pyproject.toml` for project and dependency definitions
- `uv.lock` for reproducible dependency resolution
- `.venv` for the local virtual environment

To activate the virtual environment manually in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activation is optional when commands are executed through `uv run`.

---

## Local Infrastructure

OpsLens currently uses PostgreSQL with pgvector for local development.

Start the infrastructure:

```powershell
docker compose up -d
```

Check the service status:

```powershell
docker compose ps
```

PostgreSQL should report a `healthy` status.

The pgvector extension is enabled automatically when PostgreSQL initializes a new database volume through the initialization scripts under:

```text
docker/postgres/init/
```

---

## Code Quality

### Linting

Run Ruff:

```powershell
uv run ruff check .
```

### Formatting Check

Check whether Python files are correctly formatted:

```powershell
uv run ruff format --check .
```

To automatically format Python code:

```powershell
uv run ruff format .
```

### Static Type Checking

OpsLens uses MyPy with strict type checking.

Once application source code exists, run MyPy against the appropriate source directory:

```powershell
uv run mypy <source-directory>
```

The source directory will be defined when the application package is introduced.

### Tests

Run the test suite:

```powershell
uv run pytest
```

The project follows the convention:

```text
tests/
└── test_*.py
```

It is valid for pytest to report no collected tests before application development begins.

---

## Stopping Local Infrastructure

Stop the containers:

```powershell
docker compose down
```

This removes the containers and network but preserves the PostgreSQL data volume.

To also delete local PostgreSQL data:

```powershell
docker compose down -v
```

Use `-v` carefully because it permanently removes the local database volume.

---

## Development Workflow

Start new work from an up-to-date `main` branch:

```powershell
git switch main
git pull --ff-only
git switch -c feature/<feature-name>
```

Keep changes scoped to the purpose of the feature branch.

Before opening a pull request, run the relevant validation checks:

```powershell
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest
docker compose config --quiet
docker compose ps
```

Static type checking should also be included once application source code is present.

---

## Current Local Development Stack

The Phase 1 development environment consists of:

- Python 3.12
- uv
- Ruff
- MyPy
- pytest
- Docker Desktop
- Docker Compose
- PostgreSQL 16
- pgvector

Additional infrastructure should only be introduced when required by the OpsLens architecture.