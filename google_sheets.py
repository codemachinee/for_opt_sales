from datetime import datetime

import gspread
import pytz
from gspread.exceptions import APIError
from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from configs.passwords import admin_id, loggs_acc

moscow_tz = pytz.timezone('Europe/Moscow')
admin_account = admin_id


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=3),
       retry=retry_if_exception_type((APIError, ConnectionError, TimeoutError)))
class Sheet_base:  # класс базы данных

    def __init__(self, bot, message):
        self.bot = bot
        self.message = message
        gc = gspread.service_account(filename=r'configs\pidor-of-the-day-5880592e7067.json')  # доступ к гугл табл по ключевому файлу аккаунта разраба
        # открытие таблицы по юрл адресу:
        sh = gc.open('clients_china')
        self.worksheet_base = sh.worksheet('requests')
        self.worksheet_client_base = sh.worksheet('clients_base')

    async def record_in_base(self, kategoriya: str, brand: str, model: str, quantity: str, reasons: str='Закупка оптом'):  # функция поиска и записи в базу
        try:
            worksheet_len = len(self.worksheet_base.col_values(1)) + 1  # поиск первой свободной ячейки для записи во 2 столбце
            self.worksheet_base.update(f'A{worksheet_len}:K{worksheet_len}', [[self.message.chat.id,
                                       self.message.from_user.username, self.message.from_user.first_name,
                                       self.message.from_user.last_name, None, reasons, kategoriya, brand, model,
                                                                               quantity,
                                       str(datetime.now(moscow_tz).strftime('%d.%m.%y %H:%M'))]])
        except Exception as e:
            logger.exception('Исключение вызванное google_sheet/record_in_base', e)
            await self.bot.send_message(loggs_acc, f'Исключение вызванное google_sheet/record_in_base: {e}')

    async def chec_and_record_in_client_base(self, reasons=None):  # функция поиска и записи в базу
        try:
            worksheet_len = len(self.worksheet_client_base.col_values(1)) + 1  # поиск первой свободной ячейки для записи во 2 столбце
            if str(self.message.chat.id) in self.worksheet_client_base.col_values(1):
                pass
            else:
                self.worksheet_client_base.update(f'A{worksheet_len}:E{worksheet_len}', [[self.message.chat.id,
                                                  self.message.from_user.username, self.message.from_user.first_name,
                                                  reasons, str(datetime.now(moscow_tz).strftime('%d.%m.%y %H:%M'))]])
        except Exception as e:
            logger.exception('Исключение вызванное google_sheet/chec_and_record_in_client_base', e)
            await self.bot.send_message(loggs_acc, f'Исключение вызванное google_sheet/chec_and_record_in_client_base: {e}')

    async def rasylka_v_bazu(self):  # функция рассылки постов в базы
        mess = await self.bot.send_message(self.message.chat.id, 'загрузка..🚀')
        telegram_ids_values_list = self.worksheet_client_base.col_values(1)
        telegram_names_values_list = self.worksheet_client_base.col_values(2)
        for i in range(1, len(telegram_ids_values_list)):
            try:
                await self.bot.copy_message(telegram_ids_values_list[i], self.message.chat.id, self.message.message_id)
                    #self.bot.send_message(self.worksheet.col_values(1)[i], 'Участвовать в акции?', reply_markup=kb6)
            except Exception as e:
                logger.exception('Рассылка в базу данных', f'Босс, с @{telegram_names_values_list[i]} проблема{e}')
                await self.bot.send_message(loggs_acc, f'Босс, с @{telegram_names_values_list[i]} проблема{e}')
        await self.bot.delete_message(self.message.chat.id, mess.message_id)
        await self.bot.send_message(self.message.chat.id, 'Босс, рассылка в базу клиентов выполнена ✅')

    async def get_clients(self):
        clients_list = []
        try:
            rows = self.worksheet_client_base.get_values()
            for row in rows:
                if row == rows[0]:
                    pass
                else:
                    clients_list.append(row)
            return clients_list
        except Exception as e:
            logger.exception('Исключение вызванное google_sheet/get_clients', e)
            await self.bot.send_message(loggs_acc,
                                        f'Исключение вызванное google_sheet/get_clients: {e}')



