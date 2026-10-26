import os
import asyncio
import logging
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import httpx

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN", "8228510483:AAGMYMgiKzkFg7j7_WLkfkaFHh_5xOrmJkg")
USDT_ADDRESS = os.getenv("USDT_ADDRESS", "TTjuvLaYLCUZNnq1Nj5rKF1owR5QibPxkZ")
CRYPTOCLOUD_SHOP_ID = os.getenv("CRYPTOCLOUD_SHOP_ID", "")
CRYPTOCLOUD_API_KEY = os.getenv("CRYPTOCLOUD_API_KEY", "")
CRYPTOCLOUD_WEBHOOK_SECRET = os.getenv("CRYPTOCLOUD_WEBHOOK_SECRET", "")  # опционально

SUB_PRICE_USDT = 1  # 1 USDT в месяц
FREE_HABITS_LIMIT = 3
PREMIUM_DAYS = 30

# URL-ы для CryptoCloud (замени после деплоя на Railway)
BASE_URL = os.getenv("BASE_URL", "https://your-app.railway.app")
SUCCESS_URL = f"{BASE_URL}/success"
FAILURE_URL = f"{BASE_URL}/failure"
WEBHOOK_URL = f"{BASE_URL}/webhook/cryptocloud"

# ===== STORAGE (в памяти, для демо) =====
# В продакшене лучше SQLite/PostgreSQL
users_db = {}  # user_id -> {"habits": [], "premium_until": datetime, "payment_id": str}

# ===== KEYBOARDS =====
def main_keyboard(user_id: int) -> InlineKeyboardMarkup:
    user = users_db.get(user_id, {})
    is_premium = user.get("premium_until") and user["premium_until"] > datetime.now()
    habits_count = len(user.get("habits", []))

    buttons = [
        [InlineKeyboardButton(text="➕ Добавить привычку", callback_data="add_habit")],
        [InlineKeyboardButton(text="📋 Мои привычки", callback_data="list_habits")],
    ]
    if not is_premium and habits_count >= FREE_HABITS_LIMIT:
        buttons.append([InlineKeyboardButton(text=f"💎 Премиум за {SUB_PRICE_USDT} USDT/мес", callback_data="buy_premium")])
    elif not is_premium:
        buttons.append([InlineKeyboardButton(text=f"💎 Премиум за {SUB_PRICE_USDT} USDT/мес (нелимит)", callback_data="buy_premium")])
    else:
        buttons.append([InlineKeyboardButton(text="✅ Премиум активно", callback_data="premium_info")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def habit_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнено сегодня", callback_data=f"done:{habit_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{habit_id}")],
        [InlineKeyboardButton(text="« Назад", callback_data="list_habits")]
    ])

# ===== CRYPTOCLOUD API =====
async def create_invoice(user_id: int, amount: float = SUB_PRICE_USDT) -> str | None:
    """Создаёт инвойс в CryptoCloud, возвращает URL для оплаты"""
    if not CRYPTOCLOUD_SHOP_ID or not CRYPTOCLOUD_API_KEY:
        logging.error("CryptoCloud credentials not set")
        return None

    payload = {
        "shop_id": CRYPTOCLOUD_SHOP_ID,
        "amount": amount,
        "currency": "USDT",
        "order_id": f"habit_{user_id}_{int(datetime.now().timestamp())}",
        "success_url": SUCCESS_URL,
        "failure_url": FAILURE_URL,
        "webhook_url": WEBHOOK_URL,
        "description": f"Премиум подписка HabitBot на {PREMIUM_DAYS} дней"
    }
    headers = {"Authorization": f"Bearer {CRYPTOCLOUD_API_KEY}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post("https://api.cryptocloud.plus/v1/invoice/create", json=payload, headers=headers)
            data = resp.json()
            if data.get("status") == "success":
                return data["result"]["link"]
            logging.error(f"CryptoCloud error: {data}")
    except Exception as e:
        logging.error(f"CryptoCloud request failed: {e}")
    return None

async def verify_webhook(request_body: dict, signature: str) -> bool:
    """Проверка подписи вебхука (если настроен secret)"""
    if not CRYPTOCLOUD_WEBHOOK_SECRET:
        return True  # без секрета не проверяем
    import hmac, hashlib
    expected = hmac.new(CRYPTOCLOUD_WEBHOOK_SECRET.encode(), str(request_body).encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

# ===== BOT SETUP =====
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# ===== HANDLERS =====
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {"habits": [], "premium_until": None}
    await message.answer(
        "👋 <b>HabitBot</b> — твой трекер привычек.\n\n"
        f"Бесплатно: до {FREE_HABITS_LIMIT} привычек.\n"
        f"Премиум: нелимитированно + напоминания + экспорт — {SUB_PRICE_USDT} USDT/мес.\n\n"
        "Выбирай действие:",
        reply_markup=main_keyboard(user_id)
    )

@dp.callback_query(F.data == "add_habit")
async def cb_add_habit(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = users_db.get(user_id, {})
    is_premium = user.get("premium_until") and user["premium_until"] > datetime.now()

    if not is_premium and len(user.get("habits", [])) >= FREE_HABITS_LIMIT:
        await callback.answer(f"Лимит {FREE_HABITS_LIMIT} привычек. Купи премиум!", show_alert=True)
        return

    await state.set_state("waiting_habit_name")
    await callback.message.edit_text("📝 Напиши название привычки (например: «Читать 20 мин»):")

@dp.message(F.text, flags={"state": "waiting_habit_name"})
async def process_habit_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    habit_name = message.text.strip()[:50]
    if not habit_name:
        await message.answer("Название не может быть пустым. Попробуй ещё раз:")
        return

    habit = {"id": int(datetime.now().timestamp()), "name": habit_name, "created": datetime.now().isoformat(), "done_dates": []}
    users_db.setdefault(user_id, {"habits": [], "premium_until": None})["habits"].append(habit)
    await state.clear()
    await message.answer(f"✅ Привычка «{habit_name}» добавлена!", reply_markup=main_keyboard(user_id))

@dp.callback_query(F.data == "list_habits")
async def cb_list_habits(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    habits = users_db.get(user_id, {}).get("habits", [])
    if not habits:
        await callback.message.edit_text("📭 Привычек пока нет. Добавь первую!", reply_markup=main_keyboard(user_id))
        return

    text = "📋 <b>Твои привычки:</b>\n\n"
    for h in habits:
        done_today = datetime.now().date().isoformat() in h.get("done_dates", [])
        status = "✅" if done_today else "⬜"
        text += f"{status} {h['name']}\n"

    # клавиатура со списком
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{'✅' if datetime.now().date().isoformat() in h.get('done_dates', []) else '⬜'} {h['name']}", callback_data=f"habit:{h['id']}")]
        for h in habits
    ] + [[InlineKeyboardButton(text="« В меню", callback_data="main_menu")]])
    await callback.message.edit_text(text, reply_markup=kb)

@dp.callback_query(F.data.startswith("habit:"))
async def cb_habit_detail(callback: types.CallbackQuery):
    habit_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    habit = next((h for h in users_db.get(user_id, {}).get("habits", []) if h["id"] == habit_id), None)
    if not habit:
        await callback.answer("Не найдено", show_alert=True)
        return

    done_today = datetime.now().date().isoformat() in habit.get("done_dates", [])
    text = f"📌 <b>{habit['name']}</b>\nСоздана: {habit['created'][:10]}\nСегодня: {'✅ Выполнено' if done_today else '⬜ Не выполнено'}"
    await callback.message.edit_text(text, reply_markup=habit_keyboard(habit_id))

@dp.callback_query(F.data.startswith("done:"))
async def cb_done(callback: types.CallbackQuery):
    habit_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    habit = next((h for h in users_db.get(user_id, {}).get("habits", []) if h["id"] == habit_id), None)
    if habit:
        today = datetime.now().date().isoformat()
        if today not in habit.get("done_dates", []):
            habit.setdefault("done_dates", []).append(today)
            await callback.answer("🎉 Отмечено!")
        else:
            await callback.answer("Уже отмечено сегодня")
    await cb_habit_detail(callback)

@dp.callback_query(F.data.startswith("delete:"))
async def cb_delete(callback: types.CallbackQuery):
    habit_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    users_db[user_id]["habits"] = [h for h in users_db[user_id]["habits"] if h["id"] != habit_id]
    await callback.answer("🗑 Удалено")
    await cb_list_habits(callback)

@dp.callback_query(F.data == "buy_premium")
async def cb_buy_premium(callback: types.CallbackQuery):
    await callback.answer("Создаю счёт...")
    pay_url = await create_invoice(callback.from_user.id)
    if pay_url:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"💳 Оплатить {SUB_PRICE_USDT} USDT (TRC-20)", url=pay_url)],
            [InlineKeyboardButton(text="« Назад", callback_data="main_menu")]
        ])
        await callback.message.edit_text(
            f"💎 <b>Премиум на {PREMIUM_DAYS} дней</b>\n\n"
            f"Оплата: {SUB_PRICE_USDT} USDT в сети TRC-20\n"
            f"Кошелёк: <code>{USDT_ADDRESS}</code>\n\n"
            "Нажми кнопку ниже — откроется платёжная страница CryptoCloud.\n"
            "После оплаты премиум активируется автоматически (до 1 мин).",
            reply_markup=kb
        )
    else:
        await callback.message.edit_text("❌ Ошибка создания счёта. Проверь настройки CryptoCloud.", reply_markup=main_keyboard(callback.from_user.id))

@dp.callback_query(F.data == "premium_info")
async def cb_premium_info(callback: types.CallbackQuery):
    user = users_db.get(callback.from_user.id, {})
    until = user.get("premium_until")
    if until:
        await callback.answer(f"Премиум до {until.strftime('%d.%m.%Y')}", show_alert=True)
    else:
        await callback.answer("Премиум неактивно", show_alert=True)

@dp.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: types.CallbackQuery):
    await cmd_start(callback.message)

# ===== WEBHOOK HANDLER (для Railway) =====
from aiohttp import web

async def cryptocloud_webhook(request: web.Request):
    """Вебхук CryptoCloud: payment succeeded / failed"""
    try:
        data = await request.json()
        # Проверка подписи
        signature = request.headers.get("X-Signature", "")
        if not await verify_webhook(data, signature):
            return web.Response(status=401, text="Invalid signature")

        if data.get("status") == "success" and data.get("order_id", "").startswith("habit_"):
            # order_id = habit_{user_id}_{timestamp}
            user_id = int(data["order_id"].split("_")[1])
            users_db.setdefault(user_id, {"habits": [], "premium_until": None})
            users_db[user_id]["premium_until"] = datetime.now() + timedelta(days=PREMIUM_DAYS)
            logging.info(f"Premium activated for user {user_id}")

            # Уведомим пользователя
            try:
                await bot.send_message(user_id, "🎉 <b>Премиум активирован!</b>\nТеперь у тебя нелимит привычек и экспорт данных.")
            except:
                pass

        return web.Response(text="OK")
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return web.Response(status=500, text="Error")

async def success_page(request: web.Request):
    return web.Response(text="<h1>✅ Оплата прошла успешно</h1><p>Вернись в бот — премиум активируется автоматически.</p>", content_type="text/html")

async def failure_page(request: web.Request):
    return web.Response(text="<h1>❌ Оплата не прошла</h1><p>Попробуй ещё раз или напиши в поддержку.</p>", content_type="text/html")

# ===== ENTRY POINT =====
async def start_web_server():
    app = web.Application()
    app.router.add_post("/webhook/cryptocloud", cryptocloud_webhook)
    app.router.add_get("/success", success_page)
    app.router.add_get("/failure", failure_page)
    app.router.add_get("/", lambda r: web.Response(text="HabitBot running"))

    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server started on port {port}")
    return runner

async def main():
    # Удаляем вебхук бота (используем polling)
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем веб-сервер для CryptoCloud вебхуков
    await start_web_server()

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())