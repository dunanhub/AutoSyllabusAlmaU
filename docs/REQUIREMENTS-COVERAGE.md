# Соответствие требованиям

> Проверено по исходному коду и конфигурации на 14 июня 2026 года.

Статусы:

- `done` — требование реализовано и проверяется проектом;
- `partial` — базовая реализация есть, но production-аспекты отсутствуют;
- `missing` — реализация отсутствует.

| Требование | Статус | Где реализовано | Подтверждение |
|---|---|---|---|
| JWT Authentication | done | `Backend/accounts/urls.py`, Simple JWT, `Frontend/stores/auth.ts` | Login, refresh, me; 5 auth/security API tests |
| PostgreSQL | done | `settings.py`, `Docker/docker-compose.yml` | PostgreSQL 16, persistent volume, healthcheck |
| Redis | done | `settings.py`, Compose service `redis` | DB 0 для Celery, DB 1 для cache |
| Celery | done | `syllabus_generator_system/celery.py`, `syllabuses/tasks.py` | Автообнаружение task, worker в Compose |
| Docker | done | `Docker/Backend/Dockerfile`, `Docker/Frontend/Dockerfile` | Backend и frontend images собираются |
| Docker Compose | done | `Docker/docker-compose.yml` | 5 сервисов, volumes, ports, healthchecks |
| Swagger/OpenAPI | done | `drf-spectacular`, `/api/docs/`, `/api/schema/` | Swagger UI и machine-readable schema |
| PDF Generation | done | `pdf_service.py`, Django template, WeasyPrint | Background generation, media file, RU/KZ/EN |
| PDF Download | done | `download-pdf` action | JWT-protected `FileResponse`, `%PDF` test |
| CI/CD | partial | `.github/workflows/ci.yml` | CI есть; deployment stage отсутствует |
| Unit Tests | done | `Backend/tests/` | 20 pytest tests, service и API behavior |
| Integration Tests | done | `Backend/tests/` | DRF + DB + serializer + cache + PDF interactions |
| Frontend Checks | done | CI frontend job | ESLint, Nuxt typecheck, production build |
| Caching | done | `syllabuses/cache.py`, viewset list/retrieve | 300 секунд, user-scoped versioned keys |
| Cache Invalidation | done | `SyllabusViewSet`, Celery task | Все syllabus mutations и PDF workflow |
| Background Jobs | done | `generate_syllabus_pdf_task` | Generate возвращает HTTP 202 и task ID |
| PDF Status Polling | done | preview page, Pinia store, API composable | Polling каждые 3 секунды до terminal status |
| Nested Data | done | `SyllabusSerializer` | Transactional create/update связанных таблиц |
| Ownership Permissions | done | queryset и `IsOwnerOrAdmin` | Пользователь видит свои записи, staff — все |
| CORS | done | `django-cors-headers`, settings | Origins задаются env-переменной |
| Security | partial | JWT, permissions, validators | Нет HTTPS, secrets manager; JWT в localStorage; dev server |
| Database Migrations | done | `accounts/migrations`, `syllabuses/migrations` | Модель создаётся и обновляется migrations |
| Seed Data | done | `seed_syllabuses` | Demo user и заполненный силлабус |
| Responsive UI | done | Nuxt/Vuetify components | Desktop/mobile layouts и mobile registry cards |
| Production Deployment | missing | — | Нет reverse proxy, domain, HTTPS, hosting manifest |
| Monitoring | missing | — | Нет Sentry, Prometheus, Celery dashboard или alerting |
| External API | missing | — | Сторонняя бизнес-интеграция не реализована |
| Notifications | missing | — | Email/web push после PDF generation отсутствуют |

## API endpoints

### Authentication

| Method | Endpoint | Назначение |
|---|---|---|
| POST | `/api/auth/login/` | Получить access и refresh JWT |
| POST | `/api/auth/refresh/` | Обновить access token |
| GET | `/api/auth/me/` | Получить текущего пользователя |

### Syllabuses

| Method | Endpoint | Назначение |
|---|---|---|
| GET | `/api/syllabuses/` | Список доступных силлабусов |
| POST | `/api/syllabuses/` | Создать силлабус |
| GET | `/api/syllabuses/{id}/` | Получить документ |
| PUT | `/api/syllabuses/{id}/` | Полное обновление |
| PATCH | `/api/syllabuses/{id}/` | Частичное обновление |
| DELETE | `/api/syllabuses/{id}/` | Удалить |
| POST | `/api/syllabuses/{id}/duplicate/` | Создать копию |
| POST | `/api/syllabuses/{id}/set-status/` | Изменить draft/ready |
| POST | `/api/syllabuses/{id}/generate-pdf/` | Поставить PDF-задачу |
| GET | `/api/syllabuses/{id}/pdf-status/` | Получить статус задачи |
| GET | `/api/syllabuses/{id}/download-pdf/` | Скачать готовый PDF |

### Documentation

| Method | Endpoint | Назначение |
|---|---|---|
| GET | `/api/docs/` | Swagger UI |
| GET | `/api/schema/` | OpenAPI schema |

Всего: 14 прикладных HTTP-операций и 2 documentation endpoints.

## Ограничения оценки

- GitHub Actions workflow существует, но его облачный запуск можно подтвердить только после push в GitHub.
- Coverage 94% получен последним локальным Docker-прогоном; CI не устанавливает blocking threshold.
- Integration tests работают на уровне Django/DRF. Отдельных browser E2E-тестов frontend нет.
- Compose предназначен для разработки и демонстрации.
