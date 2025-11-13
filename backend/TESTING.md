# Backend Testing — How to run tests locally and in CI

This project uses Django + pytest for backend tests. The repository contains a GitHub Actions workflow that runs the full backend test workflow on push/pull_request. This document describes how to run tests locally and how CI is configured.

Quick local run (recommended)

1. Create a virtual environment and install requirements (Makefile provided):

```bash
make install
```

2. Apply migrations:

```bash
make migrate
```

3. Run the test suite (pytest):

```bash
make pytest
```

Or run the helper script (creates venv if missing):

```bash
./scripts/run_backend_tests.sh
```

Notes and troubleshooting

- Python version: CI matrix runs Python 3.11–3.13. Use a compatible Python locally.
- Virtualenv: the Makefile creates a `venv/` in the repository root by default.
- Dependencies: `requirements.txt` contains pinned versions. If you add new dependencies, update that file.
- Database: the test workflow uses SQLite by default (Django's default). If you switch to PostgreSQL in CI, update `.github/workflows/backend-tests.yml` to set up the service.
- Migrations: Before running tests, ensure migrations are created and up-to-date. Use:

```bash
python backend/manage.py makemigrations
python backend/manage.py migrate
```

CI: GitHub Actions

- Workflow file: `.github/workflows/backend-tests.yml`
- It checks out the repo, sets up Python, installs dependencies, applies migrations and runs `pytest -q`.

If you want me to add a PostgreSQL-based CI job (for closer parity to production), tell me and I'll add it.
