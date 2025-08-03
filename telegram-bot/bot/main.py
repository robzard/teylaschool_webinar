import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.filters.command import CommandStart

from sqlalchemy.future import select

from config import BOT_TOKEN, ADMIN_IDS_LIST
from database import engine, Base, get_db
from models import User

logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Создание таблиц
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Сохранение пользователя в БД
async def save_user(user_id: int):
    async for db in get_db():
        result = await db.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalars().first()
        if not user:
            new_user = User(telegram_id=user_id)
            db.add(new_user)
            await db.commit()


# Команда /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await save_user(message.from_user.id)
    file_id = 'AgACAgIAAxkBAANEaI9VQWVGBN6q1rPc4UETDZKBLP0AAmD0MRsV3oFIPpn-N2U3NpcBAAMCAAN5AAM2BA'
    text = "Добро пожаловать в чат-бот ДВУХДНЕВНОГО ОНЛАЙН-ВЕБИНАР С ТАНЕЙ TEYLA ❤️\n\n<b>Вебинар пройдет 12 и 13 августа.</b>\n\nВ этом чат-боте мы будем напоминать вам про вебинар, чтобы вы его не пропустили 😉"
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Связаться с менеджером", url="https://t.me/Teylaschool")]
    ])
    await message.answer_photo(photo=file_id, caption=text, parse_mode='HTML', reply_markup=markup)


# Команда /send_all от админа
@dp.message(Command("send_all"))
async def cmd_send_all(message: types.Message):
    # Проверка, что команду отправил админ
    if message.from_user.id not in ADMIN_IDS_LIST:
        return await message.answer("У вас нет прав для выполнения этой команды.")

    # Проверка, что команда отправлена в ответ на сообщение
    if not message.reply_to_message:
        return await message.answer("Ответьте на сообщение, которое нужно разослать.")

    # Получаем всех пользователей
    async for db in get_db():
        result = await db.execute(select(User.telegram_id))
        users = result.scalars().all()

    # Создаем кнопку
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Связаться с менеджером", url="https://t.me/Teylaschool")]
    ])

    # Рассылка
    original_message = message.reply_to_message
    success_count = 0
    fail_count = 0

    for user_id in users:
        try:
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=original_message.chat.id,
                message_id=original_message.message_id,
                reply_markup=markup
            )
            success_count += 1
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение {user_id}: {e}")
            fail_count += 1

    await message.answer(f"Сообщение разослано!\nУспешно: {success_count}\nОшибок: {fail_count}")


# Главная функция запуска
async def main():
    await on_startup()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
