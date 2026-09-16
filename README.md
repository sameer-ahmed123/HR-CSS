# HR-CSS

Phase 1 foundations for the Corporate Support System.

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to Django at `http://localhost:8000`. Create an admin account with `python manage.py createsuperuser` to sign in.

Public users can register at `/register`. New self-registered accounts receive the `EMPLOYEE` role. The API endpoint is `POST /api/v1/auth/register/`.

Module 2 authentication endpoints include `POST /api/v1/auth/login/`, `POST /api/v1/auth/logout/`, `POST /api/v1/auth/logout-all/`, `POST /api/v1/auth/invites/`, `POST /api/v1/auth/invites/<user_id>/resend/`, `GET /api/v1/auth/invites/verify/?token=...`, and `POST /api/v1/auth/invites/accept/`. Invitations expire after 48 hours.

### Email delivery

The default development email backend is the console backend, which prints emails in the Django terminal and does not deliver them. To send real invitations, copy `backend/.env.example` to `backend/.env` or set the same environment variables in your shell. Gmail requires 2-Step Verification and a Google App Password; do not use your regular Gmail password. Restart Django after changing email settings.
