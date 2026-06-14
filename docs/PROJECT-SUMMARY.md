# Проектная статистика

> Срез проекта на 14 июня 2026 года.

## Ключевые показатели

| Показатель | Значение |
|---|---:|
| Frontend pages | 10 |
| Vue components | 22 |
| Pinia stores | 2 |
| API composables | 3 |
| Django project models | 10 |
| Проектные таблицы БД | 10 |
| Django applications | 2 |
| Прикладные HTTP operations | 14 |
| Documentation endpoints | 2 |
| Всего документируемых endpoints | 16 |
| Backend tests | 20 |
| Backend coverage | 94% |
| Docker services | 5 |
| Docker named volumes | 3 |
| GitHub Actions jobs | 2 |
| Syllabus migrations | 3 |

## Frontend stack

| Технология | Версия/роль |
|---|---|
| Nuxt | `^3.17.5`, application framework |
| Vue | `^3.5.16`, UI runtime |
| TypeScript | `^5.8.3`, strict typing |
| Vuetify | `^3.12.8`, component system |
| Pinia | `^3.0.3`, state management |
| TailwindCSS | `^6.14.0` Nuxt module, layout/print utility |
| MDI | `@mdi/js`, icons |
| qrcode.vue | QR preview |
| ESLint | static frontend checks |

Фактический Nuxt build может разрешать более новую совместимую minor/patch версию по `package-lock.json`; таблица показывает constraints из `package.json`.

## Backend stack

| Технология | Версия/роль |
|---|---|
| Python | 3.12 в Docker/CI |
| Django | 6.0.6 |
| Django REST Framework | 3.16.1 |
| Simple JWT | 5.5.1 |
| drf-spectacular | 0.29.0 |
| PostgreSQL | 16 в Docker |
| django-redis | 6.0.0 |
| Celery | 5.6.2 |
| Redis | 7 Alpine в Docker |
| WeasyPrint | 69.0 |
| pytest | 9.0.2 |
| pytest-django | 4.12.0 |
| pytest-cov | 7.0.0 |

## Страницы Frontend

1. `/`
2. `/login`
3. `/dashboard`
4. `/syllabuses`
5. `/syllabuses/create`
6. `/syllabuses/{id}`
7. `/syllabuses/{id}/edit`
8. `/templates`
9. `/analytics`
10. `/settings`

Последние три страницы являются оформленными разделами Coming Soon.

## Компоненты

### Layout — 7

- `AppHeader`
- `AppSidebar`
- `ComingSoonPage`
- `ConfirmModal`
- `EmptyState`
- `PageHeader`
- `Toast`

### Syllabus — 10

- `AssessmentTable`
- `ClassScheduleTable`
- `LearningOutcomesTable`
- `LiteratureSection`
- `PolicySection`
- `SignatureSection`
- `SyllabusForm`
- `SyllabusPreview`
- `SyllabusStatusBadge`
- `WeeklyPlanTable`

### UI — 5

- `BaseButton`
- `BaseCard`
- `BaseInput`
- `BaseSelect`
- `BaseTextarea`

Итого: 22 `.vue` компонента.

## Backend models и таблицы

1. `accounts.User`
2. `syllabuses.Syllabus`
3. `SyllabusTitleInfo`
4. `ClassScheduleRow`
5. `LearningOutcomeRow`
6. `ThematicPlanRow`
7. `AssessmentRow`
8. `LiteratureItem`
9. `CoursePolicy`
10. `SignatureBlock`

В число 10 не включены системные таблицы Django: auth permissions/groups, sessions, admin log, migrations и content types.

## API

### 14 прикладных операций

- 3 auth;
- 6 standard syllabus CRUD operations, считая PUT и PATCH отдельно;
- duplicate;
- set-status;
- generate-pdf;
- pdf-status;
- download-pdf.

### 2 documentation endpoints

- Swagger UI;
- OpenAPI schema.

Итого: 16 документируемых HTTP endpoints/operations.

## Tests

| Файл | Количество | Область |
|---|---:|---|
| `test_auth.py` | 5 | login, invalid login, refresh, me, protected API |
| `test_syllabus.py` | 8 | ownership, CRUD, duplicate, status, cache |
| `test_pdf.py` | 7 | enqueue, duplicate task, status, service, download |
| **Итого** | **20** | — |

Последний подтверждённый запуск:

```text
20 passed
Coverage: 94%
```

Coverage рассчитан командой:

```bash
pytest --cov=accounts --cov=syllabuses --cov-report=term-missing
```

## Docker

Сервисы:

1. `postgres`
2. `redis`
3. `backend`
4. `celery`
5. `frontend`

Volumes:

1. `postgres_data`
2. `redis_data`
3. `backend_media`

Открытые host ports: `3000`, `8000`, `5432`, `6379`.

## CI

GitHub Actions содержит два параллельных job:

- `backend`;
- `frontend`.

Backend использует service containers PostgreSQL и Redis. Frontend использует Node.js 20.

## Методика подсчёта

- Страницы: `.vue` файлы в `Frontend/pages`.
- Компоненты: `.vue` файлы в `Frontend/components`.
- Tests: функции `test_*` в `Backend/tests`.
- Models/tables: project models в `accounts/models.py` и `syllabuses/models.py`.
- Endpoints: HTTP method + route, а не только уникальный URL.
- Coverage: последний выполненный pytest-cov отчёт.
- Не учитываются generated directories, dependencies, Django system tables и cache artifacts.

## Уровень готовности

### Готово для демонстрации

- authentication;
- syllabus CRUD;
- preview;
- Redis cache;
- asynchronous PDF;
- Docker Compose;
- Swagger;
- tests и CI configuration.

### Требует production доработки

- deployment;
- HTTPS;
- secrets management;
- monitoring;
- Celery retries и locking;
- frontend E2E tests;
- backup policy;
- production object storage.
