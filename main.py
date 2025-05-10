import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from FSM import (
    Another_model,
    Message_from_admin,
    Next_level_base,
    Rassylka,
    anoter_model_registration,
    message_from_admin_chat,
    message_from_admin_text,
    message_from_user,
    next_level,
    rassylka,
)

from configs import passwords
from handlers import (
    check_callbacks,
    check_message,
    day_visitors,
    help,
    next_level_base,
    post,
    price,
    reset_cash,
    result,
    sent_message,
    start,
    tester,
)
from configs.passwords import codemashine_test, loggs_acc, lemonade

logger.remove()
# Настраиваем логирование в файл с ограничением количества файлов
logger.add(
    "loggs.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",
    rotation="5 MB",  # Ротация файла каждые 10 MB
    retention="10 days",  # Хранить только 5 последних логов
    compression="zip",  # Сжимать старые логи в архив
    backtrace=True,     # Сохранение трассировки ошибок
    diagnose=True       # Подробный вывод
)

# token = lemonade
token = codemashine_test

bot = Bot(token=token)
dp = Dispatcher()


dp.message.register(start, Command(commands='start'))
dp.message.register(help, Command(commands='help'))
dp.message.register(post, Command(commands='post'))
dp.message.register(sent_message, Command(commands='sent_message'))
dp.message.register(day_visitors, Command(commands='day_visitors'))
dp.message.register(reset_cash, Command(commands='reset_cash'))

dp.message.register(anoter_model_registration, Another_model.model)

dp.message.register(message_from_user, Another_model.message)

dp.message.register(rassylka, Rassylka.post)

dp.message.register(message_from_admin_chat, Message_from_admin.user_id)
dp.message.register(message_from_admin_text, Message_from_admin.message)

dp.callback_query.register(check_callbacks, Another_model.marka)
dp.callback_query.register(check_callbacks, Another_model.model)
dp.callback_query.register(check_callbacks, Rassylka.post)

dp.callback_query.register(check_callbacks, F.data)

dp.message.register(next_level, Next_level_base.nickname)

dp.message.register(check_message, F.text)


async def set_commands():
    commands = [
        BotCommand(command="start", description="запуск/перезапуск бота"),
        BotCommand(command="help", description="справка по боту"),
        BotCommand(command="price", description="расчет цены на услуги"),
        BotCommand(command="result", description="галерея с работами")
    ]
    await bot.set_my_commands(commands)


async def main():
    await db.chek_tables()
    await set_commands()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(db.delete_all_users, "cron", day_of_week='mon-sun', hour=00, misfire_grace_time=300)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        logger.info('включение бота')
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(db.close())
        logger.exception('выключение бота')
        asyncio.run(bot.send_message(loggs_acc, 'выключение бота'))
