import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import BotCommand
from loguru import logger

from assistent import get_assistant_manager
from configs.passwords import codemashine_test, loggs_acc, iamgroot
from FSM import (
    Get_admin,
    Message_from_admin,
    Next_level_base,
    Rassylka,
    message_from_admin_chat,
    message_from_admin_text,
    message_from_user,
    rassylka,
    count_price_step_one, count_price_step_two, handler_user_message_info
)
from functions import clients_base
from google_sheets import get_sheet_base
from handlers import (
    check_callbacks,
    day_visitors,
    handler_user_message,
    help,
    menu,
    post,
    reset_cash,
    sent_message,
    start, reload_tables,
)
from redis_file import redis_storage

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

token = iamgroot
# token = codemashine_test

bot = Bot(token=token)
dp = Dispatcher()


dp.message.register(start, Command(commands='start'))
dp.message.register(help, Command(commands='help'))
dp.message.register(menu, Command(commands='menu'))
dp.message.register(post, Command(commands='post'))
dp.message.register(reload_tables, Command(commands='reload_tables'))
dp.message.register(sent_message, Command(commands='sent_message'))
dp.message.register(day_visitors, Command(commands='day_visitors'))
dp.message.register(reset_cash, Command(commands='reset_cash'))

#
dp.message.register(message_from_user, Get_admin.message)
#
dp.message.register(rassylka, Rassylka.post)
#
dp.message.register(message_from_admin_chat, Message_from_admin.user_id)
dp.message.register(message_from_admin_text, Message_from_admin.message)

dp.callback_query.register(count_price_step_one, Next_level_base.info)
dp.message.register(count_price_step_two, Next_level_base.quantity)

dp.callback_query.register(check_callbacks, Next_level_base.kategoriya)
dp.callback_query.register(check_callbacks, Next_level_base.brand)
dp.callback_query.register(check_callbacks, Next_level_base.model)
dp.callback_query.register(check_callbacks, Next_level_base.price)
dp.callback_query.register(check_callbacks, F.data)

dp.message.register(handler_user_message_info, Next_level_base.info)
dp.message.register(handler_user_message, F.text, F.chat.type == 'private')


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
        sheet_base =  await get_sheet_base()
        await set_commands()
        await clients_base.load_base(await sheet_base.get_clients(bot))
        assistant = await get_assistant_manager()
        await assistant.initialize()
        await dp.start_polling(bot, polling_timeout=20)
    except Exception as e:
        logger.exception(f'Ошибка в боте: {e}')
    finally:
        assistant = await get_assistant_manager()
        await redis_storage.close()
        await assistant.cleanup()
        await bot.send_message(loggs_acc, 'выключение бота')


if __name__ == '__main__':
    asyncio.run(main())
