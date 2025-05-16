from datetime import datetime

from google.oauth2.service_account import Credentials
from gspread_asyncio import AsyncioGspreadClientManager
from loguru import logger
from pytz import timezone

from configs.passwords import loggs_acc

moscow_tz = timezone("Europe/Moscow")

_sheet_instance = None


def get_creds():
    return Credentials.from_service_account_file(
        "configs/pidor-of-the-day-5880592e7067.json",
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )


agcm = AsyncioGspreadClientManager(get_creds)


class SheetBase:
    def __init__(self, worksheet_base, worksheet_client_base):
        self.worksheet_base = worksheet_base
        self.worksheet_client_base = worksheet_client_base

    @classmethod
    async def create(cls):
        agc = await agcm.authorize()
        sh = await agc.open("clients_china")
        worksheet_base = await sh.worksheet("requests")
        worksheet_client_base = await sh.worksheet("clients_base")
        return cls(worksheet_base, worksheet_client_base)

    async def record_in_base(self, bot, message, kategoriya: str, brand: str, model: str, quantity: str,
                             reasons: str = 'Закупка оптом'):  # функция поиска и записи в базу
        try:
            second_column = await self.worksheet_base.col_values(1)
            worksheet_len = len(second_column) + 1  # поиск первой свободной ячейки для записи во 2 столбце
            await self.worksheet_base.update(f'A{worksheet_len}:K{worksheet_len}', [[message.chat.id,
                                       message.from_user.username, message.from_user.first_name,
                                       message.from_user.last_name, None, reasons, kategoriya, brand, model,
                                       quantity, str(datetime.now(moscow_tz).strftime('%d.%m.%y %H:%M'))]])
        except Exception as e:
            logger.exception('Исключение вызванное google_sheet/record_in_base', e)
            await bot.send_message(loggs_acc, f'Исключение вызванное google_sheet/record_in_base: {e}')

    async def chec_and_record_in_client_base(self, bot, message, reasons=None):  # функция поиска и записи в базу
        try:
            second_column = await self.worksheet_client_base.col_values(1)
            worksheet_len = len(second_column) + 1  # поиск первой свободной ячейки для записи во 2 столбце
            if str(message.chat.id) in second_column:
                pass
            else:
                await self.worksheet_client_base.update(f'A{worksheet_len}:E{worksheet_len}', [[message.chat.id,
                                                  message.from_user.username, message.from_user.first_name,
                                                  reasons, str(datetime.now(moscow_tz).strftime('%d.%m.%y %H:%M'))]])
        except Exception as e:
            logger.exception('Исключение вызванное google_sheet/chec_and_record_in_client_base', e)
            await bot.send_message(loggs_acc, f'Исключение вызванное google_sheet/chec_and_record_in_client_base: {e}')

    async def rasylka_v_bazu(self, bot, message):
        mess = await bot.send_message(message.chat.id, 'загрузка..🚀')
        ids = await self.worksheet_client_base.col_values(1)
        names = await self.worksheet_client_base.col_values(2)
        for i in range(1, len(ids)):
            try:
                await bot.copy_message(ids[i], message.chat.id, message.message_id)
            except Exception as e:
                logger.exception(f"Ошибка при отправке @{names[i]}")
                await bot.send_message(loggs_acc, f'Босс, с @{names[i]} проблема: {e}')
        await bot.delete_message(message.chat.id, mess.message_id)
        await bot.send_message(message.chat.id, 'Босс, рассылка выполнена ✅')

    async def get_clients(self, bot):
        try:
            rows = await self.worksheet_client_base.get_values()
            return [row for row in rows[1:] if row]
        except Exception as e:
            logger.exception("Ошибка в get_clients")
            await bot.send_message(loggs_acc, f'Исключение get_clients: {e}')
            return []


async def get_sheet_base():
    global _sheet_instance
    if _sheet_instance is None:
        print("Создаю новый экземпляр SheetBase...")
        _sheet_instance = await SheetBase.create()
    return _sheet_instance
