# Flask API

## Local setup

1. Create and activate a virtualenv.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables (example):

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hattrick_database
DB_USER=postgres
DB_PASSWORD=postgres
DB_SSLMODE=prefer
```

4. Run locally:

```bash
flask --app app run
```

## Deploy to Render + Supabase

This repo includes a Render Blueprint file at `render.yaml` configured for the Flask API.

### Option A: Blueprint deploy (recommended)

1. Push this repo to GitHub.
2. In Render, click **New +** -> **Blueprint**.
3. Select this repo; Render will detect `render.yaml` and create `hattrick-flask-api`.
4. In the new service, add environment variables:
   - `DATABASE_URL` = your Supabase Postgres connection string
   - `DB_SSLMODE` = `require`
5. Deploy.

### Option B: Manual web service

1. In Render, click **New +** -> **Web Service** and connect the repo.
2. Use these settings:
   - Root Directory: `flask_api`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
3. Add environment variables:
   - `DATABASE_URL` = your Supabase Postgres connection string
   - `DB_SSLMODE` = `require`
4. Deploy.

## Environment variables supported

- `DATABASE_URL` (preferred in production)
- `DB_SSLMODE` (`require` for Supabase)
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

If `DATABASE_URL` is present, the app uses it first.
