# Syllabus Generator System Backend

Backend API for the Syllabus Generator frontend.

## Local setup

```bash
cd Backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_syllabuses
python manage.py runserver 8000
```

## Environment

Use `DATABASE_URL` for PostgreSQL or set `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` separately.

If no database variables are provided, the project falls back to local SQLite for development.

## Demo user

- Email: `teacher@almau.edu.kz`
- Password: `Demo12345`

## API endpoints

Auth:
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`

Syllabuses:
- `GET /api/syllabuses/`
- `POST /api/syllabuses/`
- `GET /api/syllabuses/{id}/`
- `PUT /api/syllabuses/{id}/`
- `PATCH /api/syllabuses/{id}/`
- `DELETE /api/syllabuses/{id}/`
- `POST /api/syllabuses/{id}/duplicate/`
- `POST /api/syllabuses/{id}/set-status/`

Docs:
- `GET /api/docs/`
- `GET /api/schema/`

## Notes

- The API uses JWT authentication via Simple JWT.
- Users can only access their own syllabuses unless they are admin/staff.
