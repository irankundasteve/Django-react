# Nanox — Django + React Photography Portfolio

This repository contains a Django backend API and React frontend for the Nanox photography portfolio website.

## Tech Stack
- **Backend**: Django (JSON API for public content and protected admin CRUD)
- **Frontend**: React + Vite

## Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install django
python manage.py makemigrations api
python manage.py migrate
python manage.py runserver
```

Backend runs at `http://127.0.0.1:8000`.

### Admin API auth
Admin endpoints require header:
- `X-Admin-Token: <token>`

Default token is `nanox-admin-token` (override with env `NANOX_ADMIN_TOKEN`).

### Public API
- `GET /api/site-content/`
- `GET /api/portfolio/` (optional `?category=`)
- `GET /api/portfolio/<uuid>/`
- `GET /api/about/`
- `GET /api/services/`
- `POST /api/contact/`
- `GET /api/privacy-policy/`
- `GET /api/terms-of-service/`

### Admin API
- `POST /api/admin/portfolio/`
- `PUT|DELETE /api/admin/portfolio/<uuid>/`
- `GET|POST /api/admin/categories/`
- `PUT|DELETE /api/admin/categories/<uuid>/`
- `PUT /api/admin/about/`
- `POST /api/admin/services/`
- `PUT|DELETE /api/admin/services/<uuid>/`
- `GET /api/admin/contact/`
- `PUT|DELETE /api/admin/contact/<uuid>/`

## Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://127.0.0.1:5173`.
