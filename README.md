# Wallet Service

Небольшой сервис на **FastAPI** для работы с балансом кошельков.

Поддерживает:

* пополнение и списание средств
* конкурентно-безопасные операции
* PostgreSQL + SQLAlchemy (async)
* Alembic миграции
* Полное покрытие тестами
* Docker / docker-compose
* Healthcheck

---

## Стек

* Python 3.10
* FastAPI
* SQLAlchemy 2.x (async)
* asyncpg
* PostgreSQL 15
* Pytest
* Alembic
* Docker

---

## Архитектура

```text
app/
├── api/            # HTTP эндпоинты
├── core/           # конфигурация и DB engine
├── db/             # session, deps
├── models/         # SQLAlchemy модели
├── repositories/   # работа с БД
├── schemas/        # Pydantic схемы
├── services/       # бизнес-логика
└── main.py         # точка входа
tests/
├── conftest.py     # Фикстуры (DB, Client, Engine)
└── test_wallets.py # Интеграционные тесты API
```

---

## Переменные окружения

`.env`

```env
DATABASE_URL=postgresql+asyncpg://wallet:wallet@db:5432/wallet_db
DATABASE_URL_SYNC=postgresql://wallet:wallet@db:5432/wallet_db
```

---

## Запуск проекта

### 1. Сборка и запуск контейнеров

```bash
docker-compose up --build -d
```

### 2. Применить миграции

```bash
docker-compose exec app alembic upgrade head
```

### 3. Проверить состояние сервиса

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:

```json
{"status":"ok"}
```

---

## Тестирование

Тесты запускаются в изолированной среде внутри Docker-контейнера. Каждый тест использует чистую базу данных (благодаря автоматической очистке через TRUNCATE в фикстурах).

### Запуск тестов

```http
docker-compose exec app env PYTHONPATH=. pytest -vv
```

---

## API

### Получить баланс кошелька

```http
GET /api/v1/wallets/{wallet_id}
```

Ответ:

```json
{
  "wallet_id": "uuid",
  "balance": 1000
}
```

---

### Операция с кошельком

```http
POST /api/v1/wallets/{wallet_id}/operation
```

Тело запроса:

```json
{
  "operation_type": "DEPOSIT",
  "amount": 1000
}
```

`operation_type`:

* `DEPOSIT`
* `WITHDRAW`

---

## Конкурентность

* Используется транзакция
* Применяется `SELECT ... FOR UPDATE`
* Исключена гонка при одновременных запросах
* Гарантируется консистентность баланса

---

## Healthcheck

```http
GET /health
```

Проверяет:

* доступность приложения
* подключение к базе данных

---

## Swagger

Доступен по адресу:

```
http://localhost:8000/docs
```

---
