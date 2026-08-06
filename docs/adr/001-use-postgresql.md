# ADR-001: Use PostgreSQL as the Primary Database

## Status

Accepted

## Context

OpsLens needs to store and query:

- ML pipeline metadata
- Incident records
- Runbook content
- Agent investigation results
- Vector embeddings for semantic search

The system needs both structured SQL queries and vector similarity search.

## Decision

We will use PostgreSQL as the primary database
We will later add the pgvector extension for vector search

## Why PostgreSQL

PostgreSQL provides:

- Reliable relational data storage
- Powerful SQL querying
- Good support for production workloads
- Compatibility with pgvector
- Easy local setup using Docker
- Support from tools such as MLflow and Airflow

## Alternatives Considered

### SQLite

SQLite is simple and useful for small local applications.

It was not selected because it has limited concurrency and does not represent the production architecture we want to demonstrate.

### MySQL

MySQL is a strong relational database.

It was not selected because PostgreSQL has better support for the pgvector extension and is commonly used for AI applications that combine relational and vector data.

### MongoDB

MongoDB is flexible for document-based data.

It was not selected because OpsLens depends heavily on relational queries, joins, filtering, and structured operational metadata.

### Separate Vector Database

A separate vector database such as Chroma, FAISS, or Pinecone could be used.

For the first version, PostgreSQL with pgvector keeps the architecture simpler by storing relational and vector data in one system.

## Consequences

### Positive

- One database supports SQL and vector search
- Easier Docker-based local development
- Production-relevant technology
- Fewer services to operate initially

### Negative

- More setup than SQLite
- Vector search may be less specialized than a dedicated vector database
- PostgreSQL configuration must be managed carefully

## Review

We will reconsider this decision if:

- Vector search performance becomes insufficient
- Data volume grows significantly
- A dedicated vector database provides a clear operational advantage