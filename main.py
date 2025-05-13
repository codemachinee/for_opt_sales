import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from functions import clients_base
from google_sheets import Sheet_base
from redis_file import redis_storage

import redis

from FSM import (
    Get_admin,
    Message_from_admin,
    Next_level_base,
    Rassylka,
    message_from_admin_chat,
    message_from_admin_text,
    message_from_user,
    rassylka, save_all_user_information
)

from configs import passwords
from handlers import (
    # check_callbacks,
    day_visitors,
    help,
    post,
    reset_cash,
    sent_message,
    start,
    menu, check_callbacks
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
dp.message.register(menu, Command(commands='menu'))
dp.message.register(post, Command(commands='post'))
dp.message.register(sent_message, Command(commands='sent_message'))
dp.message.register(day_visitors, Command(commands='day_visitors'))
dp.message.register(reset_cash, Command(commands='reset_cash'))

# dp.message.register(anoter_model_registration, Another_model.model)
#
dp.message.register(message_from_user, Get_admin.message)
#
dp.message.register(rassylka, Rassylka.post)
#
dp.message.register(message_from_admin_chat, Message_from_admin.user_id)
dp.message.register(message_from_admin_text, Message_from_admin.message)

dp.callback_query.register(check_callbacks, F.data)
#
dp.message.register(check_callbacks, Next_level_base.kategoriya)
dp.message.register(check_callbacks, Next_level_base.brand)
dp.message.register(check_callbacks, Next_level_base.model)
dp.message.register(save_all_user_information, Next_level_base.quantity)

# dp.message.register(check_message, F.text)


async def set_commands():
    commands = [
        BotCommand(command="start", description="запуск/перезапуск бота"),
        BotCommand(command="menu", description="главное функциональное меню"),
        BotCommand(command="help", description="справка по боту"),

    ]
    await bot.set_my_commands(commands)


async def main():
    try:
        logger.info('включение бота')
        await set_commands()
        await clients_base.load_base(await Sheet_base(bot, None).get_clients())
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f'Ошибка в боте: {e}')
    finally:
        await redis_storage.close()
        await bot.send_message(loggs_acc, 'выключение бота')


if __name__ == '__main__':
    asyncio.run(main())
