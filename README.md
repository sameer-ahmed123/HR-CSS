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

Public users can register at `/register`. New self-registered accounts receive the `EMPLOYEE` role. The API endpoint is `POST /api/v1/auth/register/`; admin-created invitations remain available at `POST /api/v1/auth/invite/`.
