## Sahyog Bima Yojna Backend

### Setup
1) Install deps:
```
pip install -r requirements.txt
```
2) Configure env (copy `ENV_EXAMPLE.txt` to `.env` or export):
```
SECRET_KEY=...
DATABASE_URL=sqlite:///sby.db
ADMIN_EMAIL=admin@sby.local
ADMIN_PASSWORD=change-me-now
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your_smtp_username
MAIL_PASSWORD=your_smtp_password_or_app_password
MAIL_DEFAULT_SENDER=admin@sby.local
MAIL_SUPPRESS_SEND=false   # set true to suppress send in dev
POLICY_INDEX_PATH=policy_store/policy.index
POLICY_META_PATH=policy_store/policy_meta.json
POLICY_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
```
3) Run migrations:
```
flask db upgrade
```
4) Start server:
```
python app.py
```

### Policy chatbot (RAG)
- Prepare docs in `backend-flask/policies/` (txt/md/pdf).
- Build index:
```
python ingest_policies.py --docs policies
```
- API search: `POST /api/policy/search { "query": "your question", "top_k": 5 }`

### Notifications
- Admin receives: new user registration pending, new transaction submitted.
- User receives: account approved, account rejected/disabled, transaction approved/rejected (includes admin note if provided).

### Notes
- Default admin auto-creates on first run if no admin exists (uses ADMIN_EMAIL/ADMIN_PASSWORD).
- Use strong secrets and SMTP app passwords in production.

