# Микросервис каталога товаров (Next.js + FastAPI + aiogram + PostgreSQL + MinIO)

Отказоустойчивый микросервисный комплекс каталога товаров с интеграцией в **Telegram Mini App (TMA)**, управлением через **aiogram 3.x бота**, хранением медиафайлов в **MinIO S3** и данных в **PostgreSQL**.

Все сервисы спроектированы в **строгой stateless-архитектуре**, поддерживают запуск в **2+ репликах** и сбалансированы обратным прокси **Nginx** по алгоритму Round-Robin с автоматическим failover.

---

## 🛠 Технологический стек

- **Frontend:** Next.js 14 (App Router, TypeScript, Tailwind CSS, Telegram WebApp SDK)
- **Backend:** FastAPI (Python 3.12, SQLAlchemy 2.0 Async, `asyncpg`, Pydantic v2)
- **Telegram Bot:** aiogram 3.x (stateless streaming в S3, Webhook / Polling, горизонтальное масштабирование)
- **База данных:** PostgreSQL 16 (таблицы `products`, `orders`, `order_items`)
- **Объектное S3-хранилище:** MinIO (с раздачей картинок через Nginx по относительному URL `/storage/products/...`)
- **Балансировщик нагрузки:** Nginx (Load Balancer & Reverse Proxy с failover)
- **Оркестрация:** Docker Compose

---

## 🚀 Быстрый старт

### 1. Настройка переменных окружения

Скопируйте пример конфигурационного файла:
```bash
cp .env.example .env
```

Отредактируйте `.env`:
```env
# 1. Токен вашего бота от @BotFather
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# 2. Telegram ID администраторов через запятую (узнайте свой ID через @userinfobot)
# Не оставляйте пустым и не ставьте "*", чтобы посторонние не имели доступа!
ADMIN_IDS=123456789,987654321

# 3. URL для Telegram Mini App (обязателен HTTPS для мобильного клиента Telegram)
# Например, через бесплатный Cloudflare Tunnel: cloudflared tunnel --url http://localhost:80
MINI_APP_URL=https://your-tunnel.trycloudflare.com

# 4. Режим бота: "polling" для локального тестирования или "webhook" для 2+ реплик
BOT_MODE=polling
WEBHOOK_HOST=https://your-tunnel.trycloudflare.com
WEBHOOK_SECRET=my-webhook-secret-token

# 5. Секретный ключ для защиты API создания товаров
ADMIN_API_KEY=tinvix_secret_admin_key_2026
```

### 2. Запуск контейнеров

Запустите проект в Docker Compose:
```bash
docker compose up -d --build
```

Все компоненты поднимутся автоматически:
- **PostgreSQL** (`postgres`) — инициализируется и проходит healthcheck.
- **MinIO S3** (`minio`) — запускается, бэкенд автоматически создает публичный бакет `products`.
- **Backend API** (`backend`) — запускается в **2 репликах** (`tinvix-backend-1`, `tinvix-backend-2`).
- **Frontend** (`frontend`) — запускается в **2 репликах** (`tinvix-frontend-1`, `tinvix-frontend-2`).
- **Telegram Bot** (`bot`) — запускается и ожидает событий.
- **Nginx** (`nginx`) — проксирует трафик на порту `80`, раздает статику, картинки `/storage/` и балансирует запросы.

---

## 🌐 Доступ к сервисам

| Сервис | Адрес | Описание |
|---|---|---|
| **Веб-каталог (Next.js)** | [http://localhost](http://localhost) | Веб-интерфейс и Telegram Mini App |
| **API Документация (Swagger)** | [http://localhost/docs](http://localhost/docs) | Интерактивная документация FastAPI |
| **Проверка здоровья (Healthcheck)** | [http://localhost/api/health](http://localhost/api/health) | Проверка БД, MinIO и текущего инстанса |
| **MinIO Console** | [http://localhost:9101](http://localhost:9101) | Web-консоль MinIO (`minioadmin` / `minioadmin`) |
| **MinIO S3 API** | [http://localhost:9100](http://localhost:9100) | Прямой S3 API порт |

---

## 🤖 Логика работы Telegram-бота

1. **Обычный пользователь:**
   - При вводе `/start` или любого текстового сообщения бот отвечает: **«У меня есть товар»**.
   - Бот предлагает кнопку **«🛍️ Открыть каталог»**, которая открывает Next.js каталог внутри Telegram Mini App.
   - Также настраивается нативная кнопка меню Telegram (`MenuButtonWebApp`).

2. **Защита прав администратора:**
   - Только пользователи, чьи ID явно указаны в `ADMIN_IDS`, могут создавать товары.
   - Посторонний пользователь при попытке нажать «Создать товар» или ввести `/create` получает отказ: `🚫 У вас нет прав администратора. Ваш Telegram ID: <id>`.

3. **Создание товара администратором:**
   - Нажимает кнопку **«➕ Создать товар»** или вводит `/create`.
   - Бот просит отправить **название и фото в одном сообщении** (caption + photo).
   - Администратор отправляет фото с подписью, например: `MacBook Pro M3`.
   - Бот в потоковом режиме (в оперативной памяти, без записи на диск) загружает изображение в MinIO S3 и сохраняет запись в PostgreSQL через защищённый API бэкенда (`X-Admin-Secret`).
   - Идемпотентность: повторная отправка того же файла Telegram не создаёт дубликатов благодаря проверке `telegram_file_id`.
   - Бот присылает подтверждение создания с ID и ссылкой на открытие в каталоге.

---

## 📱 Запуск и проверка Telegram Mini App (TMA)

Telegram Mini App требует обязательный **HTTPS** URL. Для локального тестирования внутри мобильного или десктопного клиента Telegram используйте Cloudflare Tunnel (без регистрации):

```bash
cloudflared tunnel --url http://localhost:80
```

Скопируйте полученный HTTPS-адрес (например, `https://abc-123.trycloudflare.com`):
1. Вставьте его в `.env` в параметр `MINI_APP_URL`.
2. В Telegram напишите боту [@BotFather](https://t.me/BotFather), выберите вашего бота -> `Bot Settings` -> `Menu Button` -> `Configure menu button` и укажите этот URL.
3. Перезапустите бота:
   ```bash
   docker compose restart bot
   ```

> [!NOTE]
> Фотографии товаров отдаются по относительному пути `/storage/products/<filename>` через Nginx, поэтому они **гарантированно отображаются на любых внешних мобильных устройствах**, в отличие от ссылок на `localhost`!

---

## ⚖️ Доказательство Stateless, балансировки и отказоустойчивости

### 1. Проверка балансировки Backend:
Выполните несколько запросов к эндпоинту `/api/health`:
```bash
1..4 | ForEach-Object { (curl.exe -s http://localhost/api/health | ConvertFrom-Json).instance_id }
```
**Результат:** поочередная смена идентификаторов контейнеров (`8f06d1dbbeab-1`, `5209b5539e81-1`).

### 2. Проверка заголовка `X-Handled-By`:
```bash
curl.exe -s -I http://localhost/api/health | Select-String "X-Handled-By"
```
Показывает IP конкретной реплики, обработавшей запрос (например, `172.23.0.5:8000`).

### 3. Проверка отказоустойчивости (Failover):
Остановите одну из реплик бэкенда:
```bash
docker stop tinvix-backend-1
```
Повторите запрос к каталогу `http://localhost/api/products` — сервис продолжает работать на оставшейся реплике без сбоев благодаря директиве `proxy_next_upstream` в Nginx.

### 4. Масштабирование бота (2+ экземпляра в режиме Webhook):
В файле `.env` укажите:
```env
BOT_MODE=webhook
WEBHOOK_HOST=https://your-tunnel.trycloudflare.com
```
Запустите бота в 2 репликах:
```bash
docker compose up -d --scale bot=2
```
Nginx принимает вебхуки на `/bot-webhook` и распределяет их по кластеру ботов.

---

## 🛒 Защита API и создание заказов

1. **Защита создания товаров:**
   Прямой вызов `POST /api/products` или `POST /api/products/upload` без заголовка `X-Admin-Secret` возвращает `403 Forbidden`:
   ```bash
   curl -X POST http://localhost/api/products/upload -F "title=Test"
   # Ответ: 403 Forbidden: Доступ запрещён: требуется ключ администратора
   ```

2. **Оформление заказа в PostgreSQL:**
   При нажатии кнопки «Оформить заказ» в корзине фронтенд отправляет `POST /api/orders`, сохраняя заказ с товарами в таблицах `orders` и `order_items` в PostgreSQL.

---

## 📤 Сдача проекта в форму (GitHub / GitLab)

Для отправки ссылки в форму создайте репозиторий на GitHub или GitLab и выполните:
```bash
git remote add origin https://github.com/<ваш_аккаунт>/tinvix-catalog.git
git branch -M main
git push -u origin main
```
Файл `.env` с секретными токенами надёжно исключён через `.gitignore` и в репозиторий не попадёт.
