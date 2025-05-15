import asyncio

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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

    async def new_main_menu_buttons(self):
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
        await self.bot.send_message(self.message.chat.id, f'{self.menu_level}',
                                   message_thread_id=self.message.message_thread_id, reply_markup=kb2)

    async def rasylka_buttons(self):
        kb_rasylka = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='💿 Общая база клиентов', callback_data='Общая база клиентов')],
            [InlineKeyboardButton(text='❌ Отмена', callback_data="Основное меню")]])
        await self.bot.send_message(text='Выберите базу для отправки рассылки:', chat_id=self.message.chat.id,
                                         reply_markup=kb_rasylka)
