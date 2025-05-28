import json
from datetime import datetime
from typing import Optional

import aiofiles
from google.oauth2.service_account import Credentials
from gspread import service_account
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
        try:
            agc = await agcm.authorize()
            sh = await agc.open("clients_china")
            worksheet_base = await sh.worksheet("requests")
            worksheet_client_base = await sh.worksheet("clients_base")
            return cls(worksheet_base, worksheet_client_base)
        except Exception as e:
            logger.exception('Исключение вызванное google_sheet/create', e)

    async def record_in_base(self, bot, message, kategoriya: str, brand: str, model: str, quantity: str,
                             end_price: str | None = None, reasons: str = 'Закупка оптом'):  # функция поиска и записи в базу
        try:
            second_column = await self.worksheet_base.col_values(1)
            worksheet_len = len(second_column) + 1  # поиск первой свободной ячейки для записи во 2 столбце
            await self.worksheet_base.update(f'A{worksheet_len}:L{worksheet_len}', [[message.chat.id,
                                       message.chat.username, message.chat.first_name,
                                       message.chat.last_name, None, reasons, kategoriya, brand, model,
                                       quantity, end_price, str(datetime.now(moscow_tz).strftime('%d.%m.%y %H:%M'))]])
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
                                                  message.chat.username, message.chat.first_name,
                                                  reasons, str(datetime.now(moscow_tz).strftime('%d.%m.%y %H:%M'))]])
        except Exception as e:
            logger.exception('Исключение вызванное google_sheet/chec_and_record_in_client_base', e)
            await bot.send_message(loggs_acc, f'Исключение вызванное google_sheet/chec_and_record_in_client_base: {e}')

    async def rasylka_v_bazu(self, bot, message):
        mess = await bot.send_message(message.chat.id, 'Загрузка..🚀')
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
    try:
        global _sheet_instance
        if _sheet_instance is None:
            print("Создаю новый экземпляр SheetBase...")
            _sheet_instance = await SheetBase.create()
        return _sheet_instance
    except Exception as e:
        logger.exception(f"get_sheet_base: {e}")


def data_updater():
    try:
        gc = service_account(filename="configs/pidor-of-the-day-5880592e7067.json")

        sheet_urls = [
            "https://docs.google.com/spreadsheets/d/1p4xQXqozQugy3NaHut3TUY6COqvzCgYb2AEMV1Cx6Zc/edit?gid=1677852760#gid=1677852760", #phoneholder
            "https://docs.google.com/spreadsheets/d/1s2dyd9fHWVtBJLGWO4JT2AUskRXvUaFwFFrh1ikp8i0/edit?gid=121557587#gid=121557587", #otg/hub
            "https://docs.google.com/spreadsheets/d/1xfIx2SMaWnR88xPWY2tZ0fzLVTes2D8HMWxZBtbXGFs/edit?gid=1007442373#gid=1007442373", #powerbanks
            "https://docs.google.com/spreadsheets/d/1HISN8oq8UawoT721ckVDYYTIJCoA0p0VtZ8wYXB25Po/edit?gid=1733893965#gid=1733893965", #wireless charger
            "https://docs.google.com/spreadsheets/d/1_IxmDysMNlruynERjTqcfKrLdSPS9Va3WlzLLB92g_M/edit?gid=818698707#gid=818698707", #carcharger
            'https://docs.google.com/spreadsheets/d/1nYUr1-Zb_m9sBvJzUO4n8v-f5v9GYgCZQeqxaQg-2LY/edit?gid=1733893965#gid=1733893965', #CPU,GPU,SSD, MB
            'https://docs.google.com/spreadsheets/d/1It_UPBuqvJSdxQhV_yGRh_CeZTJblEta4dH4p-KQOUs/edit?gid=1677852760#gid=1677852760', #everycom
            'https://docs.google.com/spreadsheets/d/1IbLXLZteFidJ0jqW5Hq1b9Z0GTgyB-cYPou_4oV1_-4/edit?gid=1246518664#gid=1246518664', #Аудио кабели/ Переходники, Наушники
            'https://docs.google.com/spreadsheets/d/1ZquUFSa6qpZ_SrEyfSvUPXxEjah0d8jwmhJ2Ic-oMmI/edit?gid=832962407#gid=832962407', #Зарядки с проводами
            'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBAIqBBwzgSyw2zMSiso-c0js6lFI/edit?gid=0#gid=0', #сетевые фильтры
            'https://docs.google.com/spreadsheets/d/1lc1tBWMCSOGKwdM-U6C7U1R3lRJLsUX99FCVAsaax5E/edit?gid=0#gid=0', #наушники
            'https://docs.google.com/spreadsheets/d/1pyO8MjxutwF-lQUv6qC7uqlWijEZ0xGHTMOOEQ6RWMY/edit?gid=1623276324#gid=1623276324' #провода

        ]

        full_data = {}

        for url in sheet_urls:
            sh = gc.open_by_url(url)
            worksheet = sh.sheet1
            values = worksheet.get_all_values()
            headers = values[0]
            for row in values[1:]:
                row_dict = dict(zip(headers, row))
                model = row_dict.get("Модель", "").strip()
                article = row_dict.get("Артикул товара", "").strip()
                if model and article:
                    key = f'{article}__{model}'
                    full_data[key] = row_dict

        # Сохраняем в файл
        with open("local_data/products.json", "w", encoding="utf-8") as f:
            json.dump(full_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.exception(f"data_updater: {e}")


async def find_product(query: str) -> Optional[list]:
    try:
        product_list = []
        async with aiofiles.open("local_data/products.json", "r", encoding="utf-8") as f:
            content = await f.read()
            products_db = json.loads(content)
        if query in products_db:
            product_list.append(products_db[query])
            return product_list
        else:
            for key, value in products_db.items():
                if query.upper() in key.upper():
                    product_list.append(value)

            return product_list if product_list else None
    except Exception as e:
        logger.exception(f"find_product: {e}")


data_updater()