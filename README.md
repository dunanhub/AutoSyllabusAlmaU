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

## Полный запуск проекта

### Быстрый запуск через Docker

Рекомендуемый способ запуска — из корня проекта через `Docker/docker-compose.yml`.

```powershell
docker compose -f Docker/docker-compose.yml up --build
```

После запуска откройте:

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:8000/api>
- Swagger: <http://localhost:8000/api/docs>
- OpenAPI schema: <http://localhost:8000/api/schema>

Демонстрационный пользователь:

- Email: [teacher@almau.edu.kz](mailto:teacher@almau.edu.kz)
- Password: `Demo12345`

### Создание env-файлов

В проекте используются два env-файла:

- `Backend/.env` — настройки Django, PostgreSQL, Redis, Celery и Gemini;
- `Frontend/.env` — URL backend API для Nuxt.

Если файлов ещё нет, создайте их вручную или скопируйте из примеров:

```powershell
Copy-Item Backend/.env.example Backend/.env
Copy-Item Frontend/.env.example Frontend/.env
```

Для запуска через Docker заполните `Backend/.env` так:

```env
DEBUG=1
SECRET_KEY=dev-secret-key-syllabus-generator-2026
ALLOWED_HOSTS=localhost,127.0.0.1,backend
DATABASE_URL=postgres://syllabus_user:syllabus_password@postgres:5432/syllabus_db
CORS_ALLOWED_ORIGINS=http://localhost:3000

CACHE_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Заполните `Frontend/.env` так:

```env
NUXT_PUBLIC_API_URL=http://localhost:8000/api
```

Важно: при запуске через Docker backend находится внутри контейнера, поэтому PostgreSQL и Redis доступны по именам сервисов `postgres` и `redis`.

Если backend запускается локально без Docker, используйте `localhost`:

```env
DATABASE_URL=postgres://syllabus_user:syllabus_password@localhost:5432/syllabus_db
CACHE_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Как получить Gemini API Key

Gemini используется backend-частью для AI-дозаполнения и перевода шаблонов. Ключ нельзя хранить в GitHub или вставлять в README.

1. Откройте Google AI Studio: <https://aistudio.google.com/>.
2. Войдите через Google аккаунт.
3. Откройте раздел **Get API key** или перейдите напрямую: <https://aistudio.google.com/app/apikey>.
4. Нажмите **Create API key**.
5. Выберите существующий Google Cloud project или создайте новый.
6. Скопируйте созданный ключ.
7. Вставьте ключ в `Backend/.env`:

```env
GEMINI_API_KEY=PASTE_YOUR_KEY_HERE
GEMINI_MODEL=gemini-2.5-flash
```

8. Убедитесь, что реальный `.env` не коммитится в Git. В репозиторий можно добавлять только `.env.example`.
9. После изменения ключа перезапустите backend и celery:

```powershell
docker compose -f Docker/docker-compose.yml restart backend celery
```

Если появляется ошибка `429 RESOURCE_EXHAUSTED`, это означает превышение лимита Gemini free tier. Нужно подождать, сменить модель, подключить billing или использовать другой ключ. Это не ошибка кода проекта.

### Команды проверки

Backend через Docker:

```powershell
docker compose -f Docker/docker-compose.yml run --rm backend python manage.py check
docker compose -f Docker/docker-compose.yml run --rm backend pytest
```

Frontend локально:

```powershell
cd Frontend
npm run typecheck
npm run lint
npm run build
```

Полный перезапуск Docker:

```powershell
docker compose -f Docker/docker-compose.yml down
docker compose -f Docker/docker-compose.yml up --build
```

Перезапуск только backend и celery после изменения `Backend/.env`:

```powershell
docker compose -f Docker/docker-compose.yml restart backend celery
```

### Частые проблемы

- **Frontend не обновляется после изменения кода**  
  Hot reload включён через polling. Если менялись `nuxt.config.ts`, `package.json` или `.env`, перезапустите frontend-контейнер.

- **Gemini translation/document generation failed**  
  Проверьте `GEMINI_API_KEY` в `Backend/.env`, перезапустите `backend` и `celery`, затем проверьте лимиты Gemini.

- **Backend не видит PostgreSQL**  
  Для Docker используйте host `postgres`. Для локального запуска используйте host `localhost`.

- **Redis или Celery не работает**  
  Убедитесь, что сервис `redis` запущен, проверьте `CELERY_BROKER_URL`, затем перезапустите `celery`.

- **PDF/DOCX не скачивается**  
  Сначала нажмите **Сгенерировать документы**, дождитесь статуса `generated`. Если раньше была ошибка генерации, сгенерируйте документы заново.

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
| `GEMINI_API_KEY` | API key Google Gemini для AI-дозаполнения и перевода |
| `GEMINI_MODEL` | Модель Gemini, по умолчанию `gemini-2.5-flash` |

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
