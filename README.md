# Delivery Service (FastAPI)

Микросервис для регистрации посылок и расчёта стоимости доставки.

## Запуск (Docker)
1) Создай файл `.env` на основе `.env.example`.
2) Запусти сервис и зависимости:
```bash
docker compose up -d --build
```

Сервис будет доступен:
- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

## Миграции
Миграции накатываются вручную (если нужно):
```bash
docker exec -it delivery-web poetry run alembic upgrade head
```

Проверить текущую ревизию:
```bash
docker exec -it delivery-web poetry run alembic current
```

## API (пример работы с cookie-сессией)
Важно: сервис идентифицирует пользователя по cookie `session_id`.
Чтобы сохранять одну и ту же сессию между запросами, используйте cookie-jar.

### Получить типы посылок
```bash
curl -4 -s http://127.0.0.1:8000/api/package-types
```

### Зарегистрировать посылку (создаст cookies.txt)
```bash
curl -4 -c cookies.txt -H "Content-Type: application/json" \
  -d '{"name":"T-shirt","weight":1.2,"package_type_id":1,"content_value_usd":30}' \
  http://127.0.0.1:8000/api/packages
```

### Получить список своих посылок
```bash
curl -4 -b cookies.txt "http://127.0.0.1:8000/api/packages?limit=20&offset=0"
```

Фильтры:
- `package_type_id` — фильтр по типу
- `priced=true|false` — только рассчитанные/не рассчитанные

Пример:
```bash
curl -4 -b cookies.txt "http://127.0.0.1:8000/api/packages?priced=false"
```

### Получить посылку по id (только в рамках своей сессии)
```bash
curl -4 -b cookies.txt http://127.0.0.1:8000/api/packages/<PACKAGE_ID>
```

## Расчёт стоимости доставки
Стоимость доставки вычисляется по формуле:
`(weight_kg * 0.5 + content_value_usd * 0.01) * usd_rub_rate`

Курс USD/RUB берётся с https://www.cbr-xml-daily.ru/daily_json.js и кешируется в Redis.

### Ручной запуск расчёта (для отладки)
Через API:
```bash
curl -4 -X POST http://127.0.0.1:8000/api/debug/recalculate-delivery
```

Или разовым запуском scheduler-контейнера:
```bash
docker compose run --rm -e SCHEDULER_RUN_ONCE=1 scheduler
```

## Логи
Посмотреть логи web:
```bash
docker logs -f delivery-web
```

Посмотреть логи scheduler:
```bash
docker logs -f delivery-scheduler
```
