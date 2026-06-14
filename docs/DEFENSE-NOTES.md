# Материалы для защиты Syllabus Generator System

> Версия для защиты: 14 июня 2026 года.

## Краткий сценарий выступления

1. Обозначить проблему ручной подготовки силлабусов.
2. Показать целевую аудиторию и основные сценарии.
3. Объяснить разделение Nuxt frontend, Django API и инфраструктуры.
4. Продемонстрировать login, registry, создание или редактирование.
5. Запустить PDF generation и показать переход `processing → generated`.
6. Открыть Swagger и кратко показать API.
7. Показать Docker Compose, тесты и GitHub Actions.
8. Завершить ограничениями и roadmap.

Рекомендуемая продолжительность: 7–10 минут.

## Проблема

Силлабус — это большой структурированный академический документ. При ручной работе в Word или разрозненных таблицах возникают типовые проблемы:

- разные версии одного документа;
- неодинаковая структура у преподавателей;
- ошибки в таблицах и обязательных разделах;
- сложность повторного использования материалов;
- ручная подготовка PDF;
- отсутствие централизованного доступа и статусов готовности;
- невозможность интегрировать процесс с другими университетскими системами.

## Решение

Syllabus Generator System переводит силлабус в структурированную модель данных и предоставляет единый рабочий процесс:

- аутентификация преподавателя;
- реестр его документов;
- форма с академическими разделами и динамическими таблицами;
- автосохранение;
- статусы `draft/ready`;
- копирование существующего силлабуса;
- HTML preview будущего документа;
- фоновая генерация и защищённое скачивание PDF;
- воспроизводимый запуск всей системы.

## Использованные технологии

### Почему Django и DRF

Django предоставляет зрелую ORM, migrations, security middleware, admin infrastructure и устойчивую экосистему. DRF сокращает объём кода для REST API, serializers, permissions и viewsets. Для проекта с большим числом связанных таблиц это надёжнее ручной SQL-обвязки.

### Почему Nuxt 3

Nuxt задаёт понятную структуру Vue-приложения: file-based routing, layouts, middleware, plugins и runtime config. TypeScript снижает риск несовпадения API-модели и формы. Nuxt подходит как для текущего SPA-подобного интерфейса, так и для последующего SSR/production развития.

### Почему Vuetify

Vuetify предоставляет единые accessible-компоненты: navigation drawer, dialog, data table, form controls, chips, buttons и responsive behavior. Это позволяет поддерживать корпоративную визуальную систему без собственной реализации каждого состояния UI.

### Почему Pinia

Pinia хранит состояние пользователя и силлабусов между страницами, инкапсулирует API-операции и упрощает синхронизацию после CRUD или PDF polling.

### Почему PostgreSQL

Силлабус содержит множество связанных сущностей и требует транзакций, ограничений и надёжного постоянного хранения. PostgreSQL хорошо подходит для реляционной модели и дальнейшего роста нагрузки.

### Почему Redis

Redis выполняет две независимые роли:

- быстрый cache list/detail ответов в logical DB 1;
- broker и result backend Celery в logical DB 0.

Разделение logical databases предотвращает смешивание cache keys и queue data.

### Почему Celery

PDF generation занимает больше времени, чем обычный CRUD request. Celery выносит эту работу из HTTP request, поэтому backend быстро возвращает `202 Accepted`, а пользователь продолжает работать и наблюдает статус.

### Почему WeasyPrint

WeasyPrint строит PDF из HTML/CSS. Один шаблон удобно поддерживать для таблиц, кириллицы, казахских символов, page breaks, repeating headers и page numbers.

### Почему Docker

Docker фиксирует версии runtime и системных библиотек WeasyPrint. Compose одной командой поднимает backend, frontend, database, Redis и worker, уменьшая различия между машинами разработчиков.

## Самые сложные части проекта

### JWT flow

Frontend хранит пару access/refresh, прикладывает access к запросам и при 401 делает одну попытку refresh. Route middleware защищает внутренние страницы, а backend по умолчанию требует authenticated user.

### Nested serializers

Силлабус состоит из one-to-one секций и ordered collections. Serializer извлекает вложенные данные, выполняет основную mutation и синхронизирует дочерние строки внутри transaction. Это обеспечивает целостность документа.

### PDF generation

Сервис должен повторно загрузить все связи, подготовить литературу, отрендерить академический HTML, корректно обработать Unicode, сохранить файл и состояние ошибки. Повторная генерация заменяет старый файл после успешного рендера.

### Redis cache

Кэш нельзя делать общим для всех пользователей. Ключ содержит user ID и versioned namespace. Инвалидация повышает версию, поэтому старые ключи автоматически перестают использоваться.

### Celery workflow

Система сохраняет task ID и статус `processing`, не допускает повторной постановки того же документа и завершает workflow статусом `generated` или `failed`.

### Docker orchestration

Backend и worker должны дождаться healthy PostgreSQL и Redis, использовать одинаковые env и совместный media volume. Иначе worker создал бы файл, недоступный backend-контейнеру.

## Что реализовано сверх CRUD

- custom user с email как идентификатором;
- JWT login, refresh и profile endpoint;
- owner/admin permissions;
- nested transactional document model;
- автосохранение frontend;
- дублирование силлабуса;
- управление статусом готовности;
- completion indicator;
- user-scoped Redis cache;
- автоматическая cache invalidation;
- асинхронная PDF generation;
- persisted task и PDF statuses;
- frontend polling;
- protected binary download;
- Swagger/OpenAPI;
- demo seed command;
- responsive интерфейс и dark/light theme;
- Docker healthchecks и persistent volumes;
- pytest, coverage и GitHub Actions.

## Демонстрационный сценарий

1. Запустить `docker compose -f Docker/docker-compose.yml up --build`.
2. Открыть <http://localhost:3000>.
3. Войти как `teacher@almau.edu.kz`.
4. Показать dashboard и реестр.
5. Открыть «История Казахстана».
6. Перейти в edit и изменить описание.
7. Сохранить и показать обновлённый preview.
8. Запустить PDF.
9. Объяснить HTTP 202, Redis queue и Celery worker.
10. Дождаться статуса «PDF готов» и скачать файл.
11. Открыть Swagger.
12. Показать результат `pytest` и CI workflow.

## Ограничения текущей версии

- Docker использует development server Django и Nuxt;
- нет HTTPS и reverse proxy;
- нет production secrets manager;
- JWT хранится в `localStorage`;
- нет frontend browser E2E tests;
- нет task retry/backoff и distributed lock;
- нет мониторинга Celery, API и ошибок;
- нет role matrix кроме owner/staff;
- media не вынесено в S3-совместимое object storage;
- CI не выполняет deployment.

## Что улучшить в будущем

1. Production deployment с Nginx, Gunicorn/Uvicorn и HTTPS.
2. Secrets management и раздельные settings по окружениям.
3. HttpOnly cookies либо усиленная token security.
4. Sentry, metrics, structured logs и Celery monitoring.
5. Retry/backoff и timeout PDF-задач.
6. Email/in-app уведомления о готовности PDF.
7. Роли преподавателя, координатора, декана и администратора.
8. Workflow согласования и история версий.
9. Библиотека утверждённых шаблонов.
10. Экспорт DOCX и интеграция с LMS.
11. Object storage для PDF и подписей.
12. Playwright/Cypress E2E tests.
13. Автоматический deployment из CI.

## Возможные вопросы преподавателя

### 1. Какую проблему решает проект?

Он стандартизирует подготовку силлабусов, хранит документ как структурированные данные, автоматизирует PDF и создаёт основу для академического workflow.

### 2. Почему выбран PostgreSQL?

Данные имеют выраженную реляционную структуру: один syllabus связан с титульной информацией, политиками и множеством ordered rows. PostgreSQL обеспечивает транзакции, foreign keys, надёжность и удобный рост схемы.

### 3. Почему нельзя было хранить всё одним JSON?

JSON упростил бы первую версию, но усложнил бы ограничения, выборки, администрирование, миграции отдельных секций и аналитику. Связанные таблицы лучше выражают доменную модель.

### 4. Зачем Redis, если есть PostgreSQL?

PostgreSQL является источником истины. Redis хранит временные быстрые данные: API cache и очередь Celery. Он не заменяет основную базу.

### 5. Что именно кэшируется?

Список силлабусов и detail response на 300 секунд. Dashboard отдельного backend endpoint не имеет и вычисляется на frontend.

### 6. Как предотвращается утечка данных через кэш?

Cache key содержит ID пользователя. Даже одинаковый URL для двух пользователей создаёт разные ключи.

### 7. Как работает инвалидация кэша?

Ключ содержит версию namespace. После любой mutation версия увеличивается. Новые запросы формируют ключи с новой версией и не читают устаревшие ответы.

### 8. Почему Celery нужен для PDF?

Рендер HTML, fonts и больших таблиц может занимать секунды. Фоновая задача освобождает HTTP worker и позволяет сразу вернуть пользователю task ID.

### 9. Как frontend узнаёт, что PDF готов?

После запуска он вызывает `/pdf-status/` каждые три секунды. Polling прекращается при `generated` или `failed`.

### 10. Что будет при повторном клике Generate?

Если документ уже в `processing` и имеет task ID, backend возвращает существующую задачу и не ставит дубликат.

### 11. Что происходит при ошибке PDF?

Модель получает `failed` и `pdf_error`. CRUD продолжает работать. Frontend показывает ошибку, а пользователь может повторить генерацию.

### 12. Как работает JWT?

Login возвращает короткоживущий access и refresh token. Access подписывает API-запросы. При истечении frontend использует refresh для получения нового access.

### 13. Как защищены данные разных преподавателей?

Queryset фильтруется по owner, а object permission проверяет owner или staff status. Клиентский ID сам по себе не даёт доступа.

### 14. Что такое nested serializer в этом проекте?

Это serializer, который одновременно принимает основную запись syllabus и связанные секции. Он преобразует один API payload в несколько связанных database records.

### 15. Почему вложенное обновление выполняется в transaction?

Если создание одной дочерней строки завершится ошибкой, transaction откатит весь документ и не оставит частично обновлённый syllabus.

### 16. Как формируется PDF?

Django template получает syllabus и связанные rows. WeasyPrint интерпретирует HTML/CSS и создаёт PDF, который сохраняется через Django storage.

### 17. Как поддерживаются русский и казахский языки?

HTML использует UTF-8 и Unicode-capable fonts. WeasyPrint встраивает нужные glyphs в PDF.

### 18. Зачем Docker?

Он воспроизводит Python, Node, PostgreSQL, Redis и системные библиотеки WeasyPrint. Проект запускается одинаково на разных машинах.

### 19. Зачем healthchecks в Compose?

`depends_on` без healthcheck знает только о запуске процесса, но не о готовности базы. Healthcheck не позволяет backend стартовать до готовности PostgreSQL и Redis.

### 20. Что проверяет CI?

Backend job устанавливает зависимости, поднимает PostgreSQL/Redis, применяет migrations, выполняет Django check и pytest с coverage. Frontend job выполняет npm ci, lint, typecheck и build.

### 21. Сколько тестов написано?

20 pytest-тестов: authentication, authorization, CRUD, duplicate/status, cache invalidation, background enqueue, PDF status/service/download.

### 22. Какой coverage?

Последний подтверждённый результат — 94% для приложений `accounts` и `syllabuses`. Порог не блокирует CI.

### 23. Есть ли integration tests?

Да. API tests проходят через DRF, serializers, database и cache. PDF service тестируется с реальным WeasyPrint. Полных browser E2E tests пока нет.

### 24. Почему статус ready меняется отдельным endpoint?

Это отдельная бизнес-операция, которая не изменяет содержимое и не должна инвалидировать готовый PDF. Отдельный endpoint делает правило явным.

### 25. Что происходит с PDF после редактирования?

Изменение содержимого сбрасывает PDF status в `not_generated`, очищает metadata и удаляет старый файл после успешного commit.

### 26. Почему Swagger важен?

Он делает API-контракт доступным frontend-разработчикам и проверяющим, упрощает ручное тестирование JWT endpoints и документирует binary response.

### 27. Является ли текущий Docker production-ready?

Нет. Это локальная и демонстрационная среда: используются development servers, открытые порты и dev secrets. Production требует отдельной конфигурации.

### 28. Где находится источник истины?

PostgreSQL. Pinia и Redis содержат производное или временное состояние и могут быть восстановлены из API/database.

### 29. Почему есть SQLite fallback?

Он упрощает локальные management commands и разработку без PostgreSQL. Полная Docker-среда и CI используют PostgreSQL.

### 30. Как масштабировать систему?

Backend и Celery можно масштабировать горизонтально, Redis/PostgreSQL вынести в managed services, media — в object storage, а frontend раздавать через CDN. Для PDF нужно добавить distributed lock и task limits.

## Финальная формулировка

Проект является не только CRUD-приложением. Он демонстрирует полный web-stack: typed frontend, защищённый REST API, реляционную модель, cache, background processing, document generation, контейнеризацию, automated tests и CI. Следующий этап — production hardening и академический approval workflow.
