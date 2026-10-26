# 🤖 HabitBot — Трекер привычек в Telegram с подпиской за USDT

Готовый бот за 1 вечер. Никакого кода писать не нужно — только настройки.

---

## 📋 Что делает бот

| Функция | Бесплатно | Премиум (1 USDT/мес) |
|---------|-----------|----------------------|
| Привычки | до 3 шт. | нелимитированно |
| Отметки «выполнено» | ✅ | ✅ |
| Напоминания | ❌ | ✅ (в planos) |
| Экспорт CSV | ❌ | ✅ (в planos) |
| Реклама | нет | нет |

Оплата — **USDT TRC-20** через **CryptoCloud** (без KYC, мгновенно).

---

## 🚀 Быстрый старт (5 шагов, 20 минут)

### 1. Подготовка (5 мин)

Убедись, что у тебя есть:
- [ ] **Telegram** — для бота
- [ ] **Кошелёк USDT (TRC-20)** — Trust Wallet / Tonkeeper / Binance / Bybit  
  → Адрес начинается на `T...` (пример: `TTjuvLaYLCUZNnq1Nj5rKF1owR5QibPxkZ`)
- [ ] **GitHub аккаунт** — для бесплатного хостинга на Railway

---

### 2. Создай бота в @BotFather (2 мин)

1. Открой Telegram → найди `@BotFather`
2. Напиши `/newbot`
3. Придумай имя (например: `My Habit Tracker`)
4. Придумай юзернейм (должен заканчиваться на `bot`, например: `myhabittracker_bot`)
5. **Скопируй токен** — он выглядит так:  
   `8228510483:AAGMYMgiKzkFg7j7_WLkfkaFHh_5xOrmJkg`

---

### 3. Зарегистрируйся в CryptoCloud (3 мин)

1. Зайди на **https://cryptocloud.plus** → «Регистрация» (email + пароль, **KYC не нужен**)
2. В левом меню: **Магазины** → «Создать магазин»
   - Название: `HabitBot`
   - Валюта: **USDT (TRC-20)**
   - **URL успешной оплаты:** `https://ТВОЙ-ПРОЕКТ.railway.app/success`  
     (пока поставь заглушку `https://example.com/success`, потом заменишь)
   - **URL неуспешной оплаты:** `https://ТВОЙ-ПРОЕКТ.railway.app/failure`  
     (пока `https://example.com/failure`)
   - **URL для уведомлений (вебхук):** `https://ТВОЙ-ПРОЕКТ.railway.app/webhook/cryptocloud`  
     (пока `https://example.com/webhook/cryptocloud`)
3. После создания магазина скопируй:
   - **Shop ID** (число, например `12345`)
   - **API Key** (длинная строка, начинается на `sk_live_...` или `sk_test_...`)

> ⚠️ **Важно:** После деплоя на Railway (шаг 5) вернись в CryptoCloud и замени заглушки на **реальный URL** твоего проекта!

---

### 4. Загрузи проект на GitHub (3 мин)

**Вариант А — через браузер (проще):**

1. Зайди на **github.com** → войди / зарегистрируйся
2. Нажми **+** (справа вверху) → **New repository**
   - Repository name: `habit-bot`
   - Public / Private — как хочешь
   - **НЕ** ставь галочки README / .gitignore / license
   - Нажми **Create repository**
3. На странице репозитория: **Add file** → **Upload files**
4. Перетащи **ВСЕ файлы** из папки `OneDrive\Desktop\habit-bot\` (bot.py, requirements.txt, railway.json, .env.example, README.md)
5. Нажми **Commit changes**

**Вариант Б — через GitHub Desktop (если знаешь):**
- Клонируй репозиторий → копируй файлы → commit → push

---

### 5. Деплой на Railway (5 мин)

1. Зайди на **railway.app** → «Login with GitHub»
2. Нажми **New Project** → **Deploy from GitHub repo**
3. Выбери репозиторий `habit-bot` → **Deploy Now**
4. Подожди 1–2 минуты — сборка пройдёт автоматически (NIXPACKS сам поставит Python и зависимости)
5. Когда статус станет **Active** — нажми на проект → вкладка **Settings** → **Domains** → **Generate Domain**
   - Скопируй получившийся URL, например: `https://habit-bot-production-xxxx.up.railway.app`

---

### 6. Настрой переменные окружения (2 мин)

В Railway: проект → **Variables** → **New Variable** — добавь по одной:

| Name | Value |
|------|-------|
| `BOT_TOKEN` | `8228510483:AAGMYMgiKzkFg7j7_WLkfkaFHh_5xOrmJkg` |
| `USDT_ADDRESS` | `TTjuvLaYLCUZNnq1Nj5rKF1owR5QibPxkZ` |
| `CRYPTOCLOUD_SHOP_ID` | твой Shop ID из CryptoCloud (только цифры) |
| `CRYPTOCLOUD_API_KEY` | твой API Key из CryptoCloud |
| `BASE_URL` | твой Railway URL (например `https://habit-bot-production-xxxx.up.railway.app`) |

> Railway **автоматически перезапустит** бота после добавления переменных.

---

### 7. Обнови URL в CryptoCloud (1 мин)

Вернись в **CryptoCloud → Магазины → Твой магазин → Редактировать** и замени:

- **Успешная оплата:** `https://ТВОЙ-RAILWAY-URL/success`
- **Неуспешная оплата:** `https://ТВОЙ-RAILWAY-URL/failure`
- **Вебхук:** `https://ТВОЙ-RAILWAY-URL/webhook/cryptocloud`

Сохрани.

---

### 8. Проверь! (1 мин)

1. Открой своего бота в Telegram (по юзернейму из шага 2)
2. Нажми `/start`
3. Попробуй добавить привычку → нажми «Премиум» → откроется CryptoCloud
4. Оплати тестовым USDT (или попроси друга) — премиум активируется за 10–30 сек.

---

## 📁 Структура проекта

```
habit-bot/
├── bot.py              # Основной код бота + веб-сервер для вебхуков
├── requirements.txt    # Зависимости Python
├── railway.json        # Конфиг деплоя на Railway
├── .env.example        # Пример переменных окружения
└── README.md           # Эта инструкция
```

---

## 🔧 Как менять настройки (без кода)

Открой `bot.py` в любом редакторе (Блокнот / VS Code) и измени верхние константы:

```python
SUB_PRICE_USDT = 1        # Цена подписки в USDT
FREE_HABITS_LIMIT = 3     # Лимит бесплатных привычек
PREMIUM_DAYS = 30         # Дней премиума за одну оплату
```

После изменения — закоммить в GitHub → Railway сам перезадеплоит.

---

## 💡 Как привлечь первых пользователей (бесплатно)

1. **Telegram-чаты** по привычкам / продуктивности / саморазвитию — поищи в поиске Telegram: «привычки чат», «продуктивность», «atomic habits»
2. **VC.ru / Pikabu / Reddit (r/habits, r/productivity)** — пост: «Сделал простой трекер в Telegram, бесплатно до 3 привычек, премиум за 1$ в крипте — пробуйте»
3. **Свой профиль / сторис** — скрин бота + ссылка
4. **Каталоги ботов** — @StoreBot, @tgbotstat, botlist.space (бесплатно)

**Важно:** Не спамь. Пиши: «Решал свою проблему — сделал удобный бот, может кому пригодится». Люди ценят честность.

---

## 🛡 Безопасность и нюансы

- **Токен бота** — никому не показывай. В GitHub он в Variables, а не в коде.
- **API Key CryptoCloud** — тоже только в Variables.
- Данные пользователей **в памяти** (перезапуск = сброс). Для продакшена подключи SQLite/PostgreSQL (Railway даёт бесплатную БД).
- Бот использует **polling** (не вебхук Telegram) — проще, надежнее, работает за NAT.
- CryptoCloud вебхук — **HTTPS обязателен** (Railway даёт SSL автоматически).

---

## 🆘 Типичные проблемы

| Проблема | Решение |
|----------|---------|
| Бот не отвечает | Проверь логи в Railway (вкладка **Logs**) — там будут ошибки |
| «Ошибка создания счёта» | Проверь `CRYPTOCLOUD_SHOP_ID` и `API_KEY` в Variables |
| Премиум не активируется | Проверь, что вебхук URL в CryptoCloud точно совпадает с `BASE_URL/webhook/cryptocloud` |
| Railway «Application failed to start» | Открой Logs — чаще всего не хватает переменной окружения |

---

## 📞 Поддержка

- Логи Railway: проект → **Deployments** → последний → **Logs**
- Логи бота: те же логи, ищи строки `INFO` / `ERROR`
- CryptoCloud техподдержка: в личном кабинете чат в правом нижнем углу

---

## 🎯 Следующие шаги (когда заработает)

1. **База данных** — добавь SQLite (файл `habits.db`) или PostgreSQL (Railway → New → Database → PostgreSQL)
2. **Напоминания** — `apscheduler` + `bot.send_message` по расписанию
3. **Экспорт CSV** — кнопка «Скачать прогресс» → генерируй файл в памяти → `send_document`
4. **Реферальная система** — «Приведи друга — получи 7 дней премиума»
5. **Админка** — простая панель на `/admin` для статистики

---

**Удачи! 🚀**  
Первый доллар в крипте — уже сегодня, если نشر ссылку в пару чатов.