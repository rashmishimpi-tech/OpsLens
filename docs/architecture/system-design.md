# OpsLens System Design

## Purpose

OpsLens helps ML and platform engineers investigate failed ML pipelines.

It combines structured operational data with runbooks and past incidents to produce an evidence-backed root cause analysis and a recommended fix.

## Core Request Flow

```text
User
  ↓
FastAPI
  ↓
LangGraph Agent
  │
  ├── SQL Tool
  │   └── MLflow and Airflow metadata
  │
  └── Vector Search
      └── Runbooks and past incidents
  ↓
Evidence Aggregation
  ↓
LLM Reasoning
  ↓
Root Cause + Fix Proposal
  ↓
Human Approval Gate
  ↓
Action Tool (future)