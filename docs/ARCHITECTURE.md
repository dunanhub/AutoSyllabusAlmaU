# Архитектура Syllabus Generator System

> Актуально на 14 июня 2026 года.

## Общая архитектура

Система построена как web-приложение с разделением на пользовательский интерфейс, REST API, постоянное хранилище и инфраструктурные сервисы.

- **Nuxt frontend** отображает страницы, хранит клиентское состояние в Pinia и обращается к API.
- **Django backend** реализует JWT-аутентификацию, бизнес-операции, permissions и сериализацию вложенной структуры силлабуса.
- **PostgreSQL** хранит пользователей, силлабусы и связанные разделы.
- **Redis DB 1** хранит кэш list/detail запросов.
- **Redis DB 0** используется Celery как broker и result backend.
- **Celery worker** выполняет генерацию PDF вне HTTP request.
- **WeasyPrint** преобразует Django HTML template в PDF.
- **Media volume** хранит сгенерированные файлы.

## Диаграмма архитектуры

```text
┌─────────────────────────────────────────────────────────────────┐
│ Browser                                                         │
│ Login, dashboard, editor, preview, PDF polling/download          │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP / JSON / JWT
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ Frontend: Nuxt 3 + Vue 3 + Vuetify + Pinia                      │
│ :3000                                                           │
└──────────────────────────────┬──────────────────────────────────┘
                               │ /api/*
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ Backend: Django + DRF + Simple JWT + drf-spectacular            │
│ :8000                                                           │
└──────────────┬────────────────────┬─────────────────────────────┘
               │ ORM                │ Cache / broker
               ▼                    ▼
┌─────────────────────────┐   ┌───────────────────────────────────┐
│ PostgreSQL 16           │   │ Redis 7                           │
│ users + syllabus tables │   │ DB 0: Celery, DB 1: Django cache │
└─────────────────────────┘   └────────────────┬──────────────────┘
                                              │ queued task
                                              ▼
                              ┌───────────────────────────────────┐
                              │ Celery worker                     │
                              │ PDF task → WeasyPrint             │
                              └────────────────┬──────────────────┘
                                               │ PDF
                                               ▼
                              ┌───────────────────────────────────┐
                              │ backend_media volume              │
                              └───────────────────────────────────┘
```

## Frontend

Основные слои:

- `pages/` — маршруты login, dashboard, registry, create, preview, edit и страницы-заглушки;
- `components/` — layout, UI и компоненты формы/preview;
- `stores/` — auth и syllabus state;
- `composables/` — единый HTTP client и специализированные API;
- `middleware/auth.ts` — защита внутренних страниц;
- `plugins/` — Vuetify и ранняя инициализация stores.

`useApi` добавляет JWT header и при HTTP 401 один раз пытается обновить access token через refresh token. Syllabus store синхронизирует API-ответы с Pinia.

## Backend

Backend разделён на приложения:

- `accounts` — custom user, login/refresh через Simple JWT, endpoint `me`;
- `syllabuses` — модели документа, nested serializers, permissions, cache, Celery task и PDF service;
- `syllabus_generator_system` — settings, URL routing, WSGI/ASGI и Celery application.

`SyllabusViewSet` ограничивает queryset владельцем. Staff-пользователь получает доступ ко всем документам. Object permission дополнительно проверяет владельца или admin status.

## Поток авторизации

1. Пользователь вводит email и пароль на `/login`.
2. Frontend отправляет `POST /api/auth/login/`.
3. Simple JWT возвращает access и refresh tokens.
4. Frontend сохраняет токены в `localStorage`.
5. `GET /api/auth/me/` загружает профиль.
6. Защищённые API-запросы отправляют `Authorization: Bearer <access>`.
7. При HTTP 401 frontend вызывает `POST /api/auth/refresh/`.
8. При успешном refresh запрос повторяется один раз; при ошибке выполняется logout.
9. Route middleware перенаправляет неавторизованного пользователя на `/login`.

Ограничение текущей реализации: `localStorage` доступен JavaScript, поэтому production-версия должна рассмотреть HttpOnly cookies и полноценную XSS-защиту.

## Поток создания силлабуса

1. Преподаватель открывает `/syllabuses/create`.
2. `SyllabusForm` создаёт структуру документа из десяти академических разделов.
3. После первого изменения frontend вызывает `POST /api/syllabuses/`.
4. Последующие автосохранения отправляют `PUT /api/syllabuses/{id}/`.
5. `SyllabusSerializer` создаёт или заменяет связанные строки внутри database transaction.
6. Backend назначает текущего пользователя владельцем.
7. После mutation cache namespace инвалидируется.
8. Save and Preview перенаправляет на `/syllabuses/{id}`.

## Поток редактирования и удаления

- Edit загружает `GET /api/syllabuses/{id}/`, обновляет вложенные данные и выполняет `PUT`.
- При изменении содержимого ранее созданный PDF переводится в `not_generated`.
- Смена только `draft/ready` выполняется отдельным endpoint и PDF не инвалидирует.
- Delete выполняется после пользовательского confirm dialog.
- Duplicate создаёт новый UUID, статус `draft`, completion `0` и копирует структуру документа.

## Поток генерации PDF

1. Frontend отправляет `POST /api/syllabuses/{id}/generate-pdf/`.
2. Backend присваивает `pdf_status=processing` и сохраняет `pdf_task_id`.
3. В Redis DB 0 публикуется Celery task.
4. HTTP endpoint сразу возвращает `202 Accepted`, task ID и `processing`.
5. Frontend опрашивает `GET /api/syllabuses/{id}/pdf-status/` каждые три секунды.
6. Worker повторно загружает документ с `select_related/prefetch_related`.
7. Django формирует HTML по шаблону `templates/syllabuses/pdf/syllabus_pdf.html`.
8. WeasyPrint создаёт PDF и сохраняет его в media storage.
9. Модель получает `generated`, timestamp и очищенную ошибку.
10. При исключении сохраняются `failed` и текст ошибки; предыдущий валидный файл не удаляется.
11. Frontend прекращает polling на `generated` или `failed`.
12. `GET /download-pdf/` разрешён только для статуса `generated`.

Повторный generate во время `processing` возвращает текущий task ID и не создаёт вторую задачу.

## Поток Celery

```text
DRF generate endpoint
        │
        ├─ status = processing
        └─ apply_async(task_id)
                │
                ▼
          Redis DB 0
                │
                ▼
         Celery worker
                │
                ├─ load syllabus
                ├─ render HTML
                ├─ WeasyPrint
                ├─ save media/status
                └─ invalidate cache
```

Тесты используют eager mode, поэтому задачи выполняются в тестовом процессе и не требуют отдельного worker.

## Кэширование Redis

Кэшируются:

- `GET /api/syllabuses/` — 300 секунд;
- `GET /api/syllabuses/{id}/` — 300 секунд.

Ключ включает:

- глобальную версию namespace;
- ID пользователя;
- scope `list/detail`;
- hash query string или UUID.

Это предотвращает смешивание данных разных пользователей. После create, update, delete, duplicate, set-status, запуска PDF и завершения Celery-задачи версия namespace увеличивается. Старые ключи перестают использоваться без дорогого массового поиска Redis keys.

Dashboard вычисляет статистику на frontend из списка, отдельного statistics endpoint нет.

## Модель данных

Главные проектные модели:

1. `User`;
2. `Syllabus`;
3. `SyllabusTitleInfo`;
4. `ClassScheduleRow`;
5. `LearningOutcomeRow`;
6. `ThematicPlanRow`;
7. `AssessmentRow`;
8. `LiteratureItem`;
9. `CoursePolicy`;
10. `SignatureBlock`.

Связи используют one-to-one и foreign key с cascade delete. Вложенные списки имеют `order`.

## Docker архитектура

| Контейнер | Image/build | Зависимости | Persistent storage |
|---|---|---|---|
| `syllabus_postgres` | `postgres:16` | — | `postgres_data` |
| `syllabus_redis` | `redis:7-alpine` | — | `redis_data` |
| `syllabus_backend` | `Docker/Backend/Dockerfile` | healthy PostgreSQL, Redis | source bind, `backend_media` |
| `syllabus_celery` | backend image | healthy PostgreSQL, Redis | source bind, `backend_media` |
| `syllabus_frontend` | `Docker/Frontend/Dockerfile` | backend started | source bind, node_modules volume |

Backend при старте применяет migrations, создаёт demo data и запускает Django development server. Это удобно для разработки, но не является production-конфигурацией.

## Надёжность и ограничения

- database mutations nested serializers выполняются атомарно;
- PDF создаётся в background job и не блокирует HTTP request;
- ошибки PDF не блокируют CRUD;
- Redis и PostgreSQL имеют healthcheck в Compose;
- cache и broker используют разные logical Redis databases;
- отсутствуют task retries, monitoring, rate limiting и distributed locking;
- Celery worker в dev-контейнере работает от root;
- media хранится в Docker volume, а не в object storage;
- production reverse proxy, HTTPS и deployment pipeline отсутствуют.
