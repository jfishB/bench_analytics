# CI Pipeline

Two workflows run automatically when you push code or open a pull request:

## Backend CI

Runs these checks in order:

1. **Lint** - Checks code style flake8
2. **Test** - Runs Django tests with PostgreSQL
3. **Security** - Scans for vulnerabilities (safety, bandit)

Automatically skips `venv`, `migrations`, and other package folders.

## Frontend CI

Runs these checks in order:

1. **Type Check** - Validates TypeScript
2. **Test** - Runs Jest tests
3. **Build** - Creates production bundle
4. **Security** - Runs npm audit

## Environment Variables

The workflows use GitHub secrets if you set them, otherwise they fall back to defaults from `.env.sample`:

**Backend:**

- `POSTGRES_USER` (default: appuser)
- `POSTGRES_PASSWORD` (default: secret)
- `POSTGRES_DB` (default: appdb)
- `SECRET_KEY` (default: dev-only-not-secret)

**Frontend:**

- `REACT_APP_API_URL` (default: http://localhost:8000)
- `REACT_APP_ENV` (default: test)

To add secrets: Go to **Settings → Secrets and variables → Actions** and add them there.

## Testing Locally

**Backend:**

```bash
cd backend
venv\Scripts\Activate.ps1  # Windows
pip install -r ..\requirements.txt
pip install flake8 black isort pytest pytest-django pytest-cov safety bandit

# Run checks
flake8 .
black --check .
isort --check-only .
pytest --cov
```

**Frontend:**

```bash
cd frontend
npm install
npx tsc --noEmit
npm test -- --coverage --watchAll=false
npm run build
```

## What You'll See

When you open a PR, you'll see 2 status checks:

- ✅ Backend CI
- ✅ Frontend CI

Both must pass before merging. Each workflow runs its steps sequentially, but the two workflows run in parallel.
