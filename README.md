AI Adaptive Learning Platform
=============================

Overview
--------
AI-powered adaptive learning platform with a FastAPI backend and a React + Vite frontend. The backend generates lessons/quizzes via an AI pipeline and persists generated artifacts so students see real content. The frontend supports French (`fr`) localization.

Repository layout
-----------------
- backend/: FastAPI backend (Python 3.11+, SQLAlchemy async, Alembic, asyncpg)
- frontend/: React + Vite frontend (TypeScript, Tailwind)
- docker-compose.yml: optional local services
- docs/: design and architecture notes

Prerequisites
-------------
- Python 3.11
- Node 18+ and npm
- PostgreSQL running locally (or remote)
- Optional: `gh` CLI for creating GitHub repos

Environment (backend)
---------------------
Create a `.env` at `backend/.env` with at least:

DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<port>/<db_name>
JWT_SECRET_KEY=<secret>
GROQ_API_KEY=<groq_key>
AI_USE_FALLBACK=false

Install backend deps and run
---------------------------
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # or `pip install -e .` depending on project
# run migrations
alembic upgrade head
# start server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Install frontend deps and run
----------------------------
```bash
cd frontend
npm install
npm run dev
# build
npm run build
```

Running tests
-------------
Backend (pytest):
```bash
cd backend
source .venv/bin/activate
pytest
```

Common troubleshooting
----------------------
- Ensure `backend/.env` is loaded by the backend process (the code reads `backend/.env`).
- Use Python 3.11 and install the project dependencies into the virtualenv used to run the server.
- If DB errors occur, confirm the `DATABASE_URL` and that Postgres accepts connections.

Quick developer notes
---------------------
- Student-only routes are under `/api/v1/student/*` and will return 403 for non-student roles. Teachers should use `/api/v1/teacher/*` or use the teacher preview endpoints (if implemented).
- Generated artifacts are persisted to `ai_generated_tests` and questions/quiz/lesson tables — this ensures students see persisted content.

How to upload to GitHub (commands)
----------------------------------
If the repository is not yet a GitHub repo, use either the `gh` CLI or manual git steps.

Option A — using `gh` (recommended):
```bash
# from repo root
gh repo create <your-username>/<repo-name> --public --source=. --remote=origin --push
```

Option B — manual git commands:
```bash
# from repo root
git init
git add .
git commit -m "Initial commit"
# create a remote on GitHub via web UI, then:
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

If you already have a remote and want to push current branch:
```bash
git add .
git commit -m "Update"
git push origin HEAD
```

Next steps I can do
-------------------
- Add a short CONTRIBUTING.md with local dev checklist.
- Create a GitHub repo for you (I can run `gh repo create` if you want and `gh` is configured).

File created: README.md
