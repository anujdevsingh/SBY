Sahyog Bima Yojna (SBY) – Full Stack App
========================================

Overview
--------
SBY is a full-stack (Flask + Vue 3) app for NGO contribution tracking with admin approval flows, transaction proof uploads, email notifications, and a lightweight policy search chatbot (RAG).

Key Features
------------
- User registration with admin approval gate (JWT auth).
- Admin dashboard: approve/reject users, review transactions, view stats.
- User dashboard: submit contribution proofs (screenshot), see status and totals.
- Email notifications (SMTP via Flask-Mail):
  - Admin notified on new user registration and new transaction submission.
  - User notified on account approval/rejection and transaction approval/rejection (with admin note).
- RAG policy chatbot:
  - Embeds policy docs (txt/md/pdf) into a FAISS index with sentence-transformers.
  - Endpoint `/api/policy/search` and a floating chat widget in the UI.

Tech Stack
----------
- Backend: Flask, SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Flask-Mail, FAISS, sentence-transformers.
- Frontend: Vue 3, Vite, Pinia, Vue Router, Bootstrap 5.
- DB: SQLite by default (configurable).

Project Structure
-----------------
- backend-flask/
  - app.py, config.py, models.py, routes/, migrations/, policy_index.py, ingest_policies.py, ENV_EXAMPLE.txt
- frontend-vue/
  - src/ (components, views, router, stores, services), vite.config.js

Backend Setup
-------------
1) Install dependencies:
```
cd backend-flask
pip install -r requirements.txt
```
2) Configure environment (copy `ENV_EXAMPLE.txt` to `.env` and fill values):
```
SECRET_KEY=...
DATABASE_URL=sqlite:///sby.db
ADMIN_EMAIL=...
ADMIN_PASSWORD=...
MAIL_SERVER=...
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=...
MAIL_PASSWORD=...
MAIL_DEFAULT_SENDER=...
MAIL_SUPPRESS_SEND=false
POLICY_INDEX_PATH=policy_store/policy.index
POLICY_META_PATH=policy_store/policy_meta.json
POLICY_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2   # or multilingual model
```
3) Run migrations:
```
flask db upgrade
```
4) Start the backend:
```
python app.py
```

Policy Chatbot (RAG) Ingestion
------------------------------
1) Place policy docs in `backend-flask/policies/` (txt/md/pdf). For Hindi content, consider a multilingual model, e.g.:
```
POLICY_EMBED_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2
```
2) Build the index (batching to keep memory low):
```
cd backend-flask
python ingest_policies.py --docs policies --batch-size 128
```
3) Confirm output paths: `policy_store/policy.index` and `policy_store/policy_meta.json`.
4) Restart the backend. Frontend chat widget will use `/api/policy/search`.

Frontend Setup
--------------
1) Install dependencies:
```
cd frontend-vue
npm install
```
2) Run dev server:
```
npm run dev
```
3) The floating chat widget is mounted globally via `ChatWidget.vue` and calls the policy search API.

Auth and Roles
--------------
- First or bootstrapped admin: auto-created if no admin exists, using `ADMIN_EMAIL`/`ADMIN_PASSWORD`.
- JWT auth; users must be approved (`is_approved`) and active (`is_active`) to log in.
- Admin-only routes are protected via JWT and role checks.

Notifications
-------------
- Admin: new user registration pending, new transaction submitted.
- User: account approved, account rejected/disabled, transaction approved/rejected (includes admin note).
Requires SMTP configuration (MAIL_* envs). For local testing, set `MAIL_SUPPRESS_SEND=true`.

Transactions
------------
- Users submit amount, reference, and screenshot. Admin can approve/reject with optional note.
- Totals and status displayed in dashboards; uploads served from `/uploads`.

Policy Search API
-----------------
- Endpoint: `POST /api/policy/search`
- Body: `{ "query": "your question", "top_k": 5 }`
- Returns: array of snippets with `text`, `source`, `ref`, `score`.

Environment Notes
-----------------
- To change admin credentials, update `.env` and either reseed (delete existing admin) or update the admin user in the database via `flask shell`.
- Default DB is SQLite; switch `DATABASE_URL` for production (e.g., Postgres).
- Ensure `.env` is loaded (app uses python-dotenv in `app.py`).

Testing Quicklist
-----------------
- Backend: `flask db upgrade` succeeds; `python app.py` runs.
- Frontend: `npm run dev` serves app; login/register flows work.
- Notifications: approve/reject user and transaction, verify emails (or console if suppressed).
- RAG: run ingestion, then query via chat widget and see snippets returned.

