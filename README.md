# Syllabus Generator System

Корпоративная информационная система для создания, редактирования, согласования, просмотра и подготовки силлабусов дисциплин к публикации в PDF.

> Состояние документации: 14 июня 2026 года.

## Описание проекта

Syllabus Generator System помогает преподавателям вести силлабус как структурированный электронный документ вместо набора несвязанных файлов и ручных таблиц.

Система решает следующие задачи:

- хранит силлабусы и связанные академические разделы в единой модели;
- поддерживает создание, автосохранение, редактирование, копирование и удаление документов;
- разделяет черновики и готовые силлабусы;
- формирует многостраничный PDF в фоне;
- предоставляет защищённый API и пользовательский интерфейс;
- воспроизводимо запускается через Docker Compose.

Целевая аудитория: преподаватели, академические координаторы и администраторы образовательных программ.

## Основные возможности

- JWT Authentication и обновление access token;
- разграничение доступа по владельцу силлабуса;
- полный CRUD силлабусов и вложенных разделов;
- дублирование документа и смена статуса;
- асинхронная PDF Generation через Celery и WeasyPrint;
- PostgreSQL для постоянного хранения;
- Redis Cache для list/detail запросов;
- Redis как broker и result backend Celery;
- Swagger/OpenAPI;
- Docker Deployment для локальной и демонстрационной среды;
- GitHub Actions CI;
- pytest-тесты backend и lint/typecheck/build frontend.

## Архитектура

### Frontend

- Nuxt 3 и Vue 3;
- TypeScript;
- Vuetify 3;
- Pinia;
- защищённые маршруты и API composables;
- polling статуса фоновой PDF-задачи.

### Backend

- Django 6;
- Django REST Framework;
- Simple JWT;
- вложенные serializers для разделов силлабуса;
- drf-spectacular для OpenAPI;
- WeasyPrint для PDF.

### Infrastructure

- PostgreSQL 16;
- Redis 7;
- Celery worker;
- Docker Compose;
- GitHub Actions.

Подробное описание: [Архитектура](docs/ARCHITECTURE.md).

## Структура проекта

```text
SyllabusAlmaU/
├── .github/
│   └── workflows/
│       └── ci.yml
├── Backend/
│   ├── accounts/                 # пользователь, JWT endpoints
│   ├── syllabus_generator_system/# settings, URLs, Celery application
│   ├── syllabuses/               # модели, serializers, API, cache, tasks
│   ├── templates/                # HTML-шаблон PDF
│   ├── tests/                    # pytest
│   ├── manage.py
│   ├── pytest.ini
│   └── requirements.txt
├── Docker/
│   ├── Backend/Dockerfile
│   ├── Frontend/Dockerfile
│   └── docker-compose.yml
├── Frontend/
│   ├── components/
│   ├── composables/
│   ├── layouts/
│   ├── middleware/
│   ├── pages/
│   ├── plugins/
│   ├── stores/
│   ├── types/
│   ├── nuxt.config.ts
│   └── package.json
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEFENSE-NOTES.md
│   ├── PROJECT-SUMMARY.md
│   └── REQUIREMENTS-COVERAGE.md
└── README.md
```

## Установка

### Требования

- Python 3.12;
- Node.js 20;
- npm;
- Redis для фоновой PDF-генерации;
- PostgreSQL для полного локального окружения либо SQLite для упрощённого backend-запуска;
- системные библиотеки WeasyPrint;
- Docker Desktop для рекомендуемого запуска.

### Рекомендуемый запуск через Docker

Из корня проекта:

```bash
docker compose -f Docker/docker-compose.yml up --build
```

После запуска:

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:8000/api/>
- Swagger: <http://localhost:8000/api/docs/>
- OpenAPI schema: <http://localhost:8000/api/schema/>

Остановка без удаления данных:

```bash
docker compose -f Docker/docker-compose.yml down
```

Полный сброс volumes:

```bash
docker compose -f Docker/docker-compose.yml down -v
```

### Локальный запуск Backend

```bash
cd Backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_syllabuses
python manage.py runserver 8000
```

Для фоновых задач отдельно запустите Redis и Celery:

```bash
celery -A syllabus_generator_system worker --loglevel=info
```

Если `DATABASE_URL` и `DB_*` не заданы, Django использует SQLite. Для Celery и Redis cache необходимо указать доступные Redis URL.

### Локальный запуск Frontend

```bash
cd Frontend
npm install
npm run dev
```

## Переменные окружения

Примеры находятся в `Backend/.env.example` и `Frontend/.env.example`.

### Frontend

| Переменная | Назначение | Пример |
|---|---|---|
| `NUXT_PUBLIC_API_URL` | Базовый URL Django API | `http://localhost:8000/api` |

### Backend

| Переменная | Назначение |
|---|---|
| `DEBUG` | Режим разработки Django |
| `SECRET_KEY` | Криптографический ключ Django и JWT |
| `ALLOWED_HOSTS` | Разрешённые host headers |
| `DATABASE_URL` | Полное PostgreSQL connection string |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Альтернатива `DATABASE_URL` |
| `CORS_ALLOWED_ORIGINS` | Разрешённые frontend origins |
| `CACHE_URL` | Redis cache URL, в Docker `redis://redis:6379/1` |
| `CELERY_BROKER_URL` | Celery broker, в Docker `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Хранилище результатов Celery |
| `CELERY_TASK_ALWAYS_EAGER` | Синхронное выполнение задач в тестах |
| `CELERY_TASK_EAGER_PROPAGATES` | Проброс ошибок eager-задач в тестах |

Не храните production secrets в репозитории.

## Тестовый пользователь

- Email: [teacher@almau.edu.kz](mailto:teacher@almau.edu.kz)
- Password: `Demo12345`

Пользователь и демонстрационный силлабус создаются командой `seed_syllabuses`.

## Swagger и API

- Swagger UI: <http://localhost:8000/api/docs/>
- OpenAPI schema: <http://localhost:8000/api/schema/>

Основные группы API:

- `/api/auth/` — login, refresh, текущий пользователь;
- `/api/syllabuses/` — CRUD и операции над силлабусом;
- `/generate-pdf/`, `/pdf-status/`, `/download-pdf/` — PDF workflow.

## Docker

Compose запускает пять сервисов:

| Сервис | Назначение | Порт |
|---|---|---|
| `frontend` | Nuxt development server | `3000` |
| `backend` | Django API | `8000` |
| `postgres` | PostgreSQL | `5432` |
| `redis` | Cache и Celery transport | `6379` |
| `celery` | PDF background worker | внутренний |

Это локальная и демонстрационная конфигурация. Для production нужны HTTPS, reverse proxy, production WSGI/ASGI server, secrets management и monitoring.

## CI/CD

Workflow `.github/workflows/ci.yml` запускается на `push` и `pull_request`.

- Backend job: Python 3.12, PostgreSQL, Redis, migrations, Django check, pytest и coverage.
- Frontend job: Node.js 20, `npm ci`, ESLint, TypeScript check и Nuxt build.

Workflow является CI-проверкой. Автоматический production deployment в проекте пока не настроен.

## Тестирование

Backend:

```bash
cd Backend
pytest --cov=accounts --cov=syllabuses --cov-report=term-missing
python manage.py check
```

Frontend:

```bash
cd Frontend
npm run lint
npm run typecheck
npm run build
```

Последний подтверждённый результат: 20 backend-тестов, coverage 94%.

## Документация

- [Архитектура](docs/ARCHITECTURE.md)
- [Соответствие требованиям](docs/REQUIREMENTS-COVERAGE.md)
- [Материалы для защиты](docs/DEFENSE-NOTES.md)
- [Статистика проекта](docs/PROJECT-SUMMARY.md)

## Ограничения

- production deployment отсутствует;
- HTTPS и централизованное управление секретами не настроены;
- мониторинг и Celery retry policy не добавлены;
- JWT хранится во frontend `localStorage`;
- Docker Compose использует Django development server.

## Автор проекта

- ФИО: ______________________________
- Учебная группа: ___________________
- Образовательная программа: ________
- Руководитель: _____________________
- Год: 2026
