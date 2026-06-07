# WB Marketplace API

REST API интернет-магазина на Django и Django REST Framework. Проект реализует регистрацию и JWT-авторизацию пользователей, личный баланс, товары, корзину, создание заказов из корзины и админ-панель для управления товарами.

## Быстрый запуск

```bash
docker compose up --build
```

После запуска будут доступны:

- Frontend: `http://localhost:5173/`
- Backend API: `http://localhost:8001/`
- Django admin: `http://localhost:8001/admin/`
- Swagger UI: `http://localhost:8001/api/docs/`
- ReDoc: `http://localhost:8001/api/redoc/`
- OpenAPI schema: `http://localhost:8001/api/schema/`

## Пользователи и роли

В проекте есть две основные роли.

Обычный пользователь:

- регистрируется через `POST /api/auth/register/` или через frontend;
- получает JWT через `POST /api/auth/token/`;
- смотрит свой профиль через `GET /api/auth/me/`;
- пополняет личный баланс через `POST /api/auth/me/balance/top-up/`;
- просматривает товары;
- добавляет товары в корзину;
- меняет количество товаров в корзине;
- удаляет товары из корзины;
- создает заказ из корзины;
- смотрит историю своих заказов.

Админ:

- создается автоматически при запуске Docker Compose;
- может войти в Django admin;
- может создавать, редактировать и удалять товары;
- может просматривать пользователей, корзины, заказы и позиции заказов.

Данные демо-админа:

```text
URL: http://localhost:8001/admin/
login: admin
password: admin12345
```

Учетные данные демо-админа можно переопределить через переменные окружения:

```env
DEMO_ADMIN_USERNAME=admin
DEMO_ADMIN_EMAIL=admin@example.com
DEMO_ADMIN_PASSWORD=admin12345
```

## Основные API endpoints

Авторизация и профиль:

- `POST /api/auth/register/` - регистрация пользователя;
- `POST /api/auth/token/` - получение access/refresh JWT;
- `POST /api/auth/token/refresh/` - обновление access JWT;
- `GET /api/auth/me/` - профиль текущего пользователя;
- `POST /api/auth/me/balance/top-up/` - пополнение баланса.

Товары:

- `GET /api/products/` - просмотр товаров доступен всем;
- `POST /api/products/` - создание товара, только admin/staff;
- `PUT/PATCH /api/products/{id}/` - редактирование товара, только admin/staff;
- `DELETE /api/products/{id}/` - удаление товара, только admin/staff.

Корзина:

- `GET /api/cart/` - текущая корзина пользователя;
- `POST /api/cart/items/` - добавить товар в корзину;
- `PATCH /api/cart/items/{id}/` - изменить количество;
- `DELETE /api/cart/items/{id}/` - удалить позицию;
- `DELETE /api/cart/items/clear/` - очистить корзину.

Заказы:

- `POST /api/orders/` - создать заказ из корзины;
- `GET /api/orders/` - история заказов пользователя;
- `GET /api/orders/{id}/` - детали заказа.

`POST /api/orders/` может оформить всю корзину или только выбранные позиции:

```json
{
  "cart_item_ids": [1, 2]
}
```

Если `cart_item_ids` не передать, будет оформлена вся корзина.

## Бизнес-логика заказа

Создание заказа вынесено в сервисный слой и выполняется внутри транзакции:

1. блокируются позиции корзины;
2. блокируются товары;
3. проверяются активность товаров и остатки на складе;
4. блокируется пользователь;
5. проверяется баланс;
6. списывается баланс пользователя;
7. списывается количество товаров со склада;
8. создаются заказ и позиции заказа со снапшотами названия и цены;
9. очищается корзина или выбранные позиции корзины;
10. успешный заказ логируется в консоль и файл.

Такой подход защищает от частичных списаний и гонок при одновременных заказах.

## Соответствие ТЗ

Проект закрывает требования тестового задания:

- Python 3.11+;
- Django 4+;
- Django REST Framework;
- PostgreSQL через Docker Compose;
- JWT-авторизация через Simple JWT;
- документация API через drf-spectacular;
- README с описанием проекта и запуском;
- Dockerfile и docker-compose.yml;
- базовые тесты на pytest / pytest-django;
- чистая структура проекта: `views`, `serializers`, `models`, `services`;
- пользовательская регистрация, авторизация, профиль и баланс;
- товары с названием, описанием, ценой и количеством на складе;
- управление товарами только админом;
- просмотр товаров всеми пользователями;
- корзина: добавление, удаление, изменение количества, просмотр;
- заказы из корзины с проверкой остатков и баланса;
- списание баланса и остатков при заказе;
- очистка корзины после заказа;
- логирование успешных заказов.

## Стек

- Python 3.11+
- Django 5
- Django REST Framework
- PostgreSQL
- JWT через Simple JWT
- OpenAPI через drf-spectacular
- Docker + Docker Compose
- pytest / pytest-django
- React frontend

## Локальный запуск без Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py ensure_demo_admin
python manage.py runserver
```

Для локального запуска без Docker база по умолчанию будет SQLite, если не задан `DATABASE_URL`.

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

Для dev-режима без контейнера Vite можно запускать отдельно:

```bash
cd frontend
npm install
npm run dev
```
