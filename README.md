# Delivery Service API

Микросервис для расчета стоимости международной доставки посылок.

## 🏗️ Архитектура

- **FastAPI 0.115.0+** - веб-фреймворк
- **SQLAlchemy 2.0** - ORM для MySQL
- **Redis 5.2.0** - кеширование (единый пакет, sync + async)
- **APScheduler 3.11** - периодические задачи
- **Docker Compose** - контейнеризация

## 🚀 Быстрый старт

### Локально

\`\`\`bash
# 1. Установка зависимостей
poetry install

# 2. Создать .env файл
cp .env .env.local
# Отредактировать .env.local если нужно

# 3. Запустить MySQL и Redis (локально или в Docker)
docker-compose up -d mysql redis

# 4. Запустить приложение
poetry run uvicorn src.delivery_service.main:app --reload

# 5. Открыть Swagger
# http://localhost:8000/api/docs
\`\`\`

### Docker Compose

\`\`\`bash
docker-compose up -d
docker-compose logs -f app
\`\`\`

## 📚 API Эндпоинты

### Посылки
- \`POST /api/packages\` - Зарегистрировать посылку
- \`GET /api/packages\` - Получить мои посылки
- \`GET /api/packages/{id}\` - Информация о посылке

### Типы
- \`GET /api/package-types\` - Все доступные типы

### Задачи (отладка)
- \`POST /api/tasks/calculate-rates\` - Рассчитать стоимость доставки
- \`GET /api/tasks/scheduled\` - Список запланированных задач

## 🧪 Тестирование

\`\`\`bash
# Все тесты
poetry run pytest

# С покрытием
poetry run pytest --cov=src/delivery_service tests/

# Конкретный тест
poetry run pytest tests/test_packages.py::test_create_package -v
\`\`\`

## 📋 Версии зависимостей (2026)

| Пакет | Версия | Примечание |
|-------|--------|-----------|
| Python | 3.11+ | Поддерживается |
| FastAPI | 0.115.0+ | Последняя стабильная |
| SQLAlchemy | 2.0.37+ | ORM v2 синтаксис |
| redis | 5.2.0+ | ✅ Единый пакет (sync + async) |
| Pydantic | 2.8.0+ | V2 с лучшей производительностью |

## 📝 Лицензия

MIT
