import asyncio

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from configs.passwords import loggs_acc
from structure import structure_menu


class Buttons:  # класс для создания клавиатур различных категорий товаров

    def __init__(self, bot, message, keys_dict, back_button=None, kategoriya='', menu_level='Пожалуйста выберите:'):
        self.bot = bot
        self.message = message
        self.back_button = back_button
        self.menu_level = menu_level
        self.keys_dict = keys_dict
        self.kategoriya = kategoriya

    async def menu_buttons(self):
        try:
            keys = {}
            keyboard_list = []
            keys_list = list(self.keys_dict)
            for i in keys_list:
                index = keys_list.index(i)
                button = types.InlineKeyboardButton(text=i, callback_data=f'{self.kategoriya+i}')
                keys[f'but{index}'] = button

                # Группируем кнопки попарно
                if index > 0 and index % 2 != 0:
                    previous_button = keys[f'but{index - 1}']
                    if len(i) <= 16 and len(keys_list[index - 1]) <= 16 and structure_menu["Основное меню"] != self.keys_dict:
                        keyboard_list.append([previous_button, button])
                    else:
                        keyboard_list.append([previous_button])
                        keyboard_list.append([button])
                elif index == (len(keys_list) - 1):
                    keyboard_list.append([button])
            if self.back_button is not None:
                back_button = types.InlineKeyboardButton(text="⬅️ Назад", callback_data=self.back_button)
                keyboard_list.append([back_button])
            kb2 = types.InlineKeyboardMarkup(inline_keyboard=keyboard_list, resize_keyboard=True)
            await asyncio.sleep(0.3)
            await self.bot.edit_message_text(
                text=f'{self.menu_level}', chat_id=self.message.chat.id, message_id=self.message.message_id, parse_mode='markdown')
            await asyncio.sleep(0.1)
            await self.bot.edit_message_reply_markup(chat_id=self.message.chat.id, message_id=self.message.message_id,
                                                     reply_markup=kb2)
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                logger.info('Ошибка в keyboards/menu_buttons', e)
        except Exception as e:
            logger.exception('Ошибка в keyboards/menu_buttons', e)
            await self.bot.send_message(loggs_acc, f'Ошибка в keyboards/menu_buttons: {e}')


    async def new_main_menu_buttons(self):
        try:
            keys = {}
            keyboard_list = []
            keys_list = list(self.keys_dict.keys())
            for i in keys_list:
                index = keys_list.index(i)
                button = types.InlineKeyboardButton(text=i, callback_data=i)
                keys[f'but{index}'] = button

                # Группируем кнопки попарно
                if index > 0 and index % 2 != 0:
                    previous_button = keys[f'but{index - 1}']
                    if len(i[1]) <= 16 and len(keys_list[index - 1][1]) <= 16:
                        keyboard_list.append([previous_button])
                        keyboard_list.append([button])
                    else:
                        keyboard_list.append([previous_button])
                        keyboard_list.append([button])
                elif index == (len(keys_list) - 1):
                    keyboard_list.append([button])
            kb2 = types.InlineKeyboardMarkup(inline_keyboard=keyboard_list, resize_keyboard=True)
            await asyncio.sleep(0.3)
            await self.bot.send_message(chat_id=self.message.chat.id, text=f'{self.menu_level}',
                                       message_thread_id=self.message.message_thread_id, reply_markup=kb2)
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                logger.info('Ошибка в keyboards/new_main_menu_buttons', e)
        except Exception as e:
            logger.exception('Ошибка в keyboards/menu_buttons', e)
            await self.bot.send_message(loggs_acc, f'Ошибка в keyboards/new_main_menu_buttons: {e}')

    async def rasylka_buttons(self):
        kb_rasylka = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='💿 Общая база клиентов', callback_data='Общая база клиентов')],
            [InlineKeyboardButton(text='❌ Отмена', callback_data="Основное меню")]])
        await self.bot.send_message(text='Выберите базу для отправки рассылки:', chat_id=self.message.chat.id,
                                         reply_markup=kb_rasylka)

    async def speed_find_of_product_buttons(self, product_list):
        try:
            keyboard_list = []
            if len(product_list) > 1:
                for i in product_list:
                    text_button = f"{i['Модель']} {i['Цвет']}"
                    callback_button = f"{i['Артикул товара'].strip()}__{i['Модель'].strip()}"
                    # callback_button = f"{i['Артикул товара'].strip()}__{self.message.text}"
                    button = types.InlineKeyboardButton(text=text_button, callback_data=callback_button)
                    keyboard_list.append([button])
                if self.back_button is not None:
                    back_button = types.InlineKeyboardButton(text="⬅️ Назад", callback_data=self.back_button)
                    keyboard_list.append([back_button])
                kb2 = types.InlineKeyboardMarkup(inline_keyboard=keyboard_list)
                try:
                    await self.bot.edit_message_text(text=f'{self.menu_level}', chat_id=self.message.chat.id,
                                                     message_id=self.message.message_id, parse_mode='html')
                    await asyncio.sleep(0.1)
                    await self.bot.edit_message_reply_markup(chat_id=self.message.chat.id,
                                                             message_id=self.message.message_id,
                                                             reply_markup=kb2)
                except TelegramBadRequest:
                    await self.bot.send_message(text=f'{self.menu_level}', chat_id=self.message.chat.id, reply_markup=kb2,
                                                parse_mode='html')
            else:
                self.menu_level = (f'<b>Модель:</b> {product_list[0]["Модель"]}\n'
                                   f'<b>Цвет:</b> {product_list[0]["Цвет"]}\n'
                                   f'<b>Артикул:</b> {product_list[0]["Артикул товара"]}\n'
                                   f'<b>Вес 1 шт, кг:</b> {product_list[0]["Вес 1 шт, кг"]}\n'
                                   f'<b>MOQ, шт:</b> {product_list[0]["MOQ, шт"]}\n'
                                   f'<b>Описание:</b> {product_list[0]["Описание"]}\n'
                                   f'<b>Цена,￥:</b> {product_list[0]["Цена,￥"]}\n'
                                   f'<b>Стоимость логистики за MOQ, $:</b> {product_list[0]["Стоимость логистики за MOQ, $"]}')
                text_button = f"Рассчет итоговой стоимости"
                callback_button = f"{product_list[0]['Артикул товара'].strip()}__{product_list[0]['Модель'].strip()}"
                button = types.InlineKeyboardButton(text=text_button, callback_data=callback_button)
                keyboard_list.append([button])
                if self.back_button is not None:
                    back_button = types.InlineKeyboardButton(text="⬅️ Назад", callback_data=self.back_button)
                    keyboard_list.append([back_button])
                    kb2 = types.InlineKeyboardMarkup(inline_keyboard=keyboard_list)
                    await self.bot.edit_message_text(text=f'{self.menu_level}', chat_id=self.message.chat.id,
                                                     message_id=self.message.message_id, parse_mode='html')
                    await asyncio.sleep(0.1)
                    await self.bot.edit_message_reply_markup(chat_id=self.message.chat.id,
                                                             message_id=self.message.message_id,
                                                             reply_markup=kb2)

                else:
                    cancel_button = types.InlineKeyboardButton(text="❌ Отмена", callback_data="Основное меню")
                    keyboard_list.append([cancel_button])
                    kb2 = types.InlineKeyboardMarkup(inline_keyboard=keyboard_list)
                    try:
                        await self.bot.edit_message_text(text=f'{self.menu_level}', chat_id=self.message.chat.id,
                                                         message_id=self.message.message_id, parse_mode='html')
                        await asyncio.sleep(0.1)
                        await self.bot.edit_message_reply_markup(chat_id=self.message.chat.id,
                                                                 message_id=self.message.message_id,
                                                                 reply_markup=kb2)
                    except TelegramBadRequest:
                        await self.bot.send_message(text=f'{self.menu_level}', chat_id=self.message.chat.id,
                                                    reply_markup=kb2,
                                                    parse_mode='html')
        except Exception as e:
            logger.exception('Ошибка в keyboards/speed_find_of_product_buttons', e)
            await self.bot.send_message(loggs_acc, f'Ошибка в keyboards/speed_find_of_product_buttons: {e}')

    async def zayavka_buttons(self):
        try:
            kb_zayavka = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='✅ Оформить заявку', callback_data='✅ Оформить заявку')],
                [InlineKeyboardButton(text='⬅️ В основное меню', callback_data="Основное меню")]])
            try:
                await self.bot.edit_message_text(text=f'{self.menu_level}', chat_id=self.message.chat.id,
                                                 message_id=self.message.message_id, parse_mode='html')
                await asyncio.sleep(0.1)
                await self.bot.edit_message_reply_markup(chat_id=self.message.chat.id,
                                                         message_id=self.message.message_id,
                                                         reply_markup=kb_zayavka)
            except TelegramBadRequest:
                await self.bot.send_message(text=f'{self.menu_level}', chat_id=self.message.chat.id,
                                            reply_markup=kb_zayavka, parse_mode='html')
        except Exception as e:
            logger.exception('Ошибка в keyboards/zayavka_buttons', e)
            await self.bot.send_message(loggs_acc, f'Ошибка в keyboards/zayavka_buttons: {e}')