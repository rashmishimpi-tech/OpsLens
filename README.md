# OpsLens

> An Agentic AI Platform for ML Pipeline Investigation, Root Cause Analysis, and Intelligent Remediation.

---

## Overview

OpsLens helps ML engineers investigate pipeline failures by combining:

- MLflow metadata
- Airflow logs
- Historical incidents
- Operational runbooks
- LLM reasoning

Instead of manually checking multiple dashboards, OpsLens gathers evidence, identifies probable root causes, and recommends remediation steps.

---

## Problem

When an ML pipeline fails, engineers usually need to inspect:

- MLflow
- Airflow
- Logs
- Monitoring dashboards
- Previous incidents
- Documentation

This investigation is manual, repetitive, and time-consuming.

---

## Solution

OpsLens acts as an AI investigation assistant.

It:

1. Collects evidence
2. Retrieves relevant historical incidents
3. Queries structured metadata
4. Reasons over the collected information
5. Produces an explainable diagnosis
6. Suggests the next best action

---

## High-Level Architecture

User
↓
FastAPI
↓
Agent
├── MLflow
├── Airflow
├── PostgreSQL
├── Vector Search
└── Runbooks

---

## Tech Stack

- Python
- FastAPI
- LangGraph
- PostgreSQL
- pgvector
- Docker
- MLflow
- Apache Airflow

---

## Status

🚧 Under Development