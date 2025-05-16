from datetime import datetime
from typing import Any

from aiogram.types import Message
from loguru import logger

from configs.passwords import loggs_acc
from google_sheets import get_sheet_base, moscow_tz
from redis_file import redis_storage


class Clients:
    def __init__(self):
        self.dict = {}

    async def set_clients(self, data: dict):
        try:
            self.dict[f"{data['id']}"] = {"username": data['username'], "name": data['name'],
                                          "reasons": data["reasons"], "date": data["date"]}
        except Exception as e:
            logger.exception('Исключение вызванное functions/set_clients', e)

    async def update_clients(self, id: str, key: str, value: str):
        try:
            self.dict[id][key] = value
        except Exception as e:
            logger.exception('Исключение вызванное functions/update_clients', e)

    async def get_clients(self) -> dict:
        return self.dict

    async def load_base(self, clients_list: list):
        try:
            for i in clients_list:
                data = {"id": i[0],"username": i[1], "name": i[2],
                        "reasons": i[3], "date": i[4]}
                await self.set_clients(data)
        except Exception as e:
            logger.exception('Исключение вызванное functions/load_base', e)



clients_base = Clients()


async def antispam(bot, message: Message) -> Any:
    try:
        if await redis_storage.exists(str(message.chat.id)) is True:
            if int(await redis_storage.get(str(message.chat.id))) <= 18:
                await redis_storage.incr(str(message.chat.id))
                return True
            elif 18 < int(await redis_storage.get(str(message.chat.id))) <= 21:
                await redis_storage.incr(str(message.chat.id))
                return "Предупреждение"
            else:
                await redis_storage.expire(str(message.chat.id), 3600)
                return False
        else:
            await redis_storage.set(str(message.chat.id), 0, expire=1200)
            clients_list = await clients_base.get_clients()
            if str(message.chat.id) not in clients_list:
                sheet_base = await get_sheet_base()
                await sheet_base.chec_and_record_in_client_base(bot, message)
            else:
                await clients_base.update_clients(str(message.chat.id), "date", str(datetime.now(moscow_tz).strftime('%d.%m.%y %H:%M')))
            return True
    except Exception as e:
        logger.exception('Исключение вызванное functions/antispam', e)
        await bot.send_message(loggs_acc, f'Исключение вызванное functions/antispam: {e}')



async def is_today(date_str: str) -> bool:
    try:
        input_date = datetime.strptime(date_str, "%d.%m.%y %H:%M")
        now = datetime.now()
        return input_date.date() == now.date()
    except ValueError:
        return False  # если строка не распарсилась



# asyncio.run(clients_base.load_base(asyncio.run(Sheet_base(None, None).get_clients())))
# # print(asyncio.run(clients_base.get_clients()))
#
# for i in asyncio.run(clients_base.get_clients()).values():
#     print(asyncio.run(is_today(i["date"])))
