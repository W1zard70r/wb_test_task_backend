# WB Marketplace API

REST API интернет-магазина на Django и Django REST Framework. Проект покрывает регистрацию, JWT-авторизацию,
профиль пользователя с балансом, товары, корзину и создание заказа из корзины.

## Стек

- Python 3.11+
- Django 5
- Django REST Framework
- PostgreSQL
- JWT через Simple JWT
- OpenAPI через drf-spectacular
- Docker + Docker Compose
- pytest / pytest-django

## Что уже умеет API

- Регистрация пользователя: `POST /api/auth/register/`
- Получение JWT: `POST /api/auth/token/`
- Профиль: `GET /api/auth/me/`
- Пополнение баланса: `POST /api/auth/me/balance/top-up/`
- Просмотр товаров для всех: `GET /api/products/`
- Управление товарами только для admin/staff
- Корзина пользователя: `GET /api/cart/`
- Добавление, изменение и удаление позиций корзины
- Создание заказа из корзины: `POST /api/orders/`
- История заказов пользователя: `GET /api/orders/`

## Бизнес-логика заказа

Создание заказа вынесено в сервисный слой. Операция выполняется внутри транзакции:

1. блокируются позиции корзины;
2. блокируются товары;
3. проверяются активность товаров и остатки;
4. блокируется пользователь;
5. проверяется баланс;
6. списываются баланс и остатки;
7. создаются заказ и позиции заказа со снапшотами цены и названия;
8. корзина очищается;
9. успешный заказ логируется.

Такой подход защищает от частичных списаний и гонок при одновременных заказах.

## Запуск через Docker Compose

```bash
docker-compose up --build
```

API будет доступно на `http://localhost:8001`.

Документация:

- Swagger UI: `http://localhost:8001/api/docs/`
- ReDoc: `http://localhost:8001/api/redoc/`
- OpenAPI schema: `http://localhost:8001/api/schema/`

Админ-панель:

- URL: `http://localhost:8001/admin/`
- Логин: `admin`
- Пароль: `admin12345`

Демо-админ создается автоматически при запуске Docker Compose. Учетные данные можно переопределить через `DEMO_ADMIN_USERNAME`, `DEMO_ADMIN_EMAIL`, `DEMO_ADMIN_PASSWORD`.

## Локальный запуск без Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Тесты

```bash
pytest
```

## Линтинг

```bash
ruff check .
```


## Frontend

React-клиент лежит в `frontend/`. В Docker Compose frontend собирается в отдельный nginx-контейнер и проксирует `/api` на Django API внутри Docker-сети.

```bash
docker compose up --build
```

Frontend будет доступен на `http://localhost:5173`.

Для dev-режима без контейнера Vite по-прежнему можно запускать отдельно:

```bash
cd frontend
npm install
npm run dev
```

Корзина поддерживает частичную оплату: frontend отправляет выбранные позиции в `POST /api/orders/`:

```json
{
  "cart_item_ids": [1, 2]
}
```

Если `cart_item_ids` не передать, backend сохранит старое поведение и оформит всю корзину.
