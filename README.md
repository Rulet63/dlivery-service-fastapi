# Delivery Service (FastAPI)

Микросервис для регистрации посылок и расчёта стоимости доставки.

## Запуск (Docker)

1) Создай `.env` на основе `.env.example`.
2) Запусти сервис и зависимости:
   ```bash
   docker compose up -d --build
   ```

Сервис будет доступен:
- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

## Миграции

Миграции накатываются автоматически через сервис `migrate` при `docker compose up`.

Проверить статус:
```bash
docker logs delivery-migrate
docker compose exec web poetry run alembic current
```

## API (пример с cookie-сессией)

Пользователь определяется по cookie `session_id`. Используй cookie-jar для сохранения сессии.

### Получить типы посылок
```bash
curl -s http://127.0.0.1:8000/api/package-types | jq
```

### Зарегистрировать посылку (создаст cookies.txt)
```bash
curl -c cookies.txt -H "Content-Type: application/json" \
  -d '{"name":"T-shirt","weight":1.2,"package_type_id":1,"content_value_usd":30}' \
  http://127.0.0.1:8000/api/packages | jq
```

### Получить список своих посылок
```bash
curl -b cookies.txt "http://127.0.0.1:8000/api/packages?limit=20&offset=0" | jq
```

**Фильтры:**
- `package_type_id` — по типу посылки
- `priced=true|false` — рассчитанные/не рассчитанные

```bash
curl -b cookies.txt "http://127.0.0.1:8000/api/packages?priced=false" | jq
```

### Получить посылку по id (только свою)
```bash
curl -b cookies.txt http://127.0.0.1:8000/api/packages/<PACKAGE_ID> | jq
```

## Расчёт стоимости доставки

Формула: `(weight_kg * 0.5 + content_value_usd * 0.01) * usd_rub_rate`

Курс USD/RUB из https://www.cbr-xml-daily.ru/daily_json.js → Redis (TTL).

### Ручной запуск (отладка)
```bash
curl -X POST http://127.0.0.1:8000/api/debug/recalculate-delivery | jq
```

### Разовый запуск scheduler
```bash
docker compose run --rm -e SCHEDULER_RUN_ONCE=1 scheduler
```

## Тестирование кэша (Redis → CBR fallback)

```bash
# 1) Очистить Redis
docker compose exec redis redis-cli -n 0 FLUSHDB

# 2) Создать посылку
curl -c cookies.txt -H "Content-Type: application/json" \
  -d '{"name":"Phone","weight":0.4,"package_type_id":2,"content_value_usd":600}' \
  http://127.0.0.1:8000/api/packages | jq

# 3) Пересчёт (должен пойти в CBR)
curl -X POST http://127.0.0.1:8000/api/debug/recalculate-delivery | jq

# 4) Посылка рассчитана
curl -b cookies.txt "http://127.0.0.1:8000/api/packages?limit=10&offset=0" | jq

# 5) Курс в Redis
docker compose exec redis redis-cli -n 0 GET currency:usd_rub
```

## Логи

```bash
docker logs -f delivery-web
docker logs -f delivery-scheduler
docker logs delivery-migrate
```

## Тесты

```bash
docker compose up -d --build
pytest -q
```

Покрытие: сессии, валидация, ошибки, фильтры, “Не рассчитано” → рассчитано.

## Архитектура

```
docker compose up
├── mysql (healthy) + volume mysql_data
├── redis (healthy) + volume redis_data
├── migrate → alembic upgrade head (завершается)
├── web (depends_on migrate+mysql+redis) → uvicorn 5 workers
└── scheduler (depends_on migrate+mysql+redis) → APScheduler cron */5
```

## Локальная разработка

```bash
poetry install
poetry run pre-commit install
pre-commit run --all-files
pytest -q
```
