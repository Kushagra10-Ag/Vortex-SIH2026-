# Database Migrations

BIZmate uses Flask-Migrate (Alembic) for managing database schema migrations.

### Usage:
- Generate a new migration: `flask db migrate -m "migration description"`
- Apply migrations: `flask db upgrade`
- Rollback last migration: `flask db downgrade`

The root `migrations/` directory contains active version scripts.

