import asyncio

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from configs.passwords import group_id
from structure import structure_menu

kb1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔔 Уведомление о слотах на складах', callback_data='slots')],
    [InlineKeyboardButton(text='🤖 Блокировка планировщика', callback_data='scheduler_block')],
    [InlineKeyboardButton(text='🍇 Список складов wb', callback_data='wb_warehouses')],
    [InlineKeyboardButton(text='🏠 Список моих складов', callback_data='my_warehouses')],
    [InlineKeyboardButton(text='📋 Список товаров', callback_data='goods_list')],
    [InlineKeyboardButton(text='🔙 Тарифы на возвраты', callback_data='tariffs_returns')],
    [InlineKeyboardButton(text='📦 Тарифы на коробы', callback_data='tariffs_box')],
    [InlineKeyboardButton(text='🏗️Тарифы на монопаллеты', callback_data='tariffs_pallet')],
    [InlineKeyboardButton(text='🙊 Необработанные отзывы по товарам', callback_data='feedbacks')],
    [InlineKeyboardButton(text='❓Необработанные вопросы по товарам', callback_data='questions')],
    [InlineKeyboardButton(text='📈 Отчет о поставках', callback_data='suplier_list')]])


kb_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сухой корм PREMIATO 🐕', callback_data='PREMIATO')]])

kb_back_to_reasons = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Вернуться к выбору причины', callback_data='PREMIATO')]])

kb_back_to_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Вернуться назад', callback_data='slots')]])

kb_choice_reasons = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🚚 Закупка оптом', callback_data='opt')],
    [InlineKeyboardButton(text='📦 Проблемы с упаковкой', callback_data='package')],
    [InlineKeyboardButton(text='🍇 Пришел не тот вкус', callback_data='wrong_taste')],
    [InlineKeyboardButton(text='🐕 Перевод на корм PREMIATO', callback_data='transfer')],
    [InlineKeyboardButton(text='📋 Состав корма', callback_data='structure')],
    [InlineKeyboardButton(text='❗ Прием при проблемах со здоровьем', callback_data='health')],
    [InlineKeyboardButton(text='❓ Другое', callback_data='other')],
    [InlineKeyboardButton(text='🔙 Вернуться к выбору товара', callback_data='choice_good')]
])


kb_slots_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📦 Выбор склада', callback_data='warehouse_choice')],
    [InlineKeyboardButton(text='⚙️ Настройка склада', callback_data='settings_change')],
    [InlineKeyboardButton(text='🔙 Вернуться назад', callback_data='func_menu')]
])


class Buttons:  # класс для создания клавиатур различных категорий товаров

    def __init__(self, bot, message, keys_dict, back_button=None, menu_level='Пожалуйста выберите:'):
        self.bot = bot
        self.message = message
        self.back_button = back_button
        self.menu_level = menu_level
        self.keys_dict = keys_dict

    async def menu_buttons(self):
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
                if len(i[1]) <= 16 and len(keys_list[index - 1][1]) <= 16 and structure_menu["Основное меню"] != self.keys_dict:
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
            text=f'{self.menu_level}', chat_id=self.message.chat.id, message_id=self.message.message_id)
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
        await self.bot.send_message(self.message.chat.id, 'Пожалуйста выберите интересующий пункт меню:',
                                   message_thread_id=self.message.message_thread_id, reply_markup=kb2)

    async def rasylka_buttons(self):
        kb_rasylka = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='💿 Общая база клиентов', callback_data='Общая база клиентов')],
            [InlineKeyboardButton(text='❌ Отмена', callback_data="Основное меню")]])
        await self.bot.send_message(text='Выберите базу для отправки рассылки:', chat_id=self.message.chat.id,
                                         reply_markup=kb_rasylka)

    # async def setings_buttons(self):
    #     keys = {}
    #     keyboard_list = []
    #     if len(self.subscritions_list) == len(self.keyboard_dict) == 0:
    #         await asyncio.sleep(0.3)
    #         await self.bot.edit_message_text(
    #             text='Вы не выбрали ни одного склада', chat_id=self.message.chat.id, message_id=self.message.message_id)
    #         await self.bot.edit_message_reply_markup(chat_id=self.message.chat.id, message_id=self.message.message_id,
    #                                                  reply_markup=kb_back_to_menu)
    #     else:
    #         if self.subscritions_list[0] is None:
    #             keys_list = [['📦 Типы приемки:', 'заглушка'],
    #                          ["Короба", "2"], ["Монопаллеты", "5"],
    #                          ["Суперсейф", "6"], ["QR-поставка", "отсутствует"],
    #                          ["💸 Коэффициент приемки: до 2", 'заглушка'],
    #                          ["➖", "minus"], ["➕", "plus"]]
    #         elif int(self.subscritions_list[0]) == 1:
    #             keys_list = [['📦 Типы приемки:', 'заглушка'],
    #                          ["Короба", "2"], ["Монопаллеты", "5"],
    #                          ["Суперсейф", "6"], ["QR-поставка", "отсутствует"],
    #                          [f"💸 Коэффициент приемки: до {self.subscritions_list[0]}", 'заглушка'],
    #                          ["➕", "plus"]]
    #         elif int(self.subscritions_list[0]) == 8:
    #             keys_list = [['📦 Типы приемки:', 'заглушка'],
    #                          ["Короба", "2"], ["Монопаллеты", "5"],
    #                          ["Суперсейф", "6"], ["QR-поставка", "отсутствует"],
    #                          [f"💸 Коэффициент приемки: до {self.subscritions_list[0]}", 'заглушка'],
    #                          ["➖", "minus"]]
    #         else:
    #             keys_list = [['📦 Типы приемки:', 'заглушка'],
    #                          ["Короба", "2"], ["Монопаллеты", "5"],
    #                          ["Суперсейф", "6"], ["QR-поставка", "отсутствует"],
    #                          [f"💸 Коэффициент приемки: до {self.subscritions_list[0]}", 'заглушка'],
    #                          ["➖", "minus"], ["➕", "plus"]]
    #         for i in keys_list:
    #             index = keys_list.index(i)
    #             if len(self.subscritions_list) != 0 and (f'{i[0]}' in self.subscritions_list[1] or f'{i[0]} с коробами'
    #                                                      in self.subscritions_list[1]):
    #                 button = types.InlineKeyboardButton(text=f"🔘{i[0]}", callback_data=f"settings_{i[1]}")
    #                 keys[f'but{index}'] = button
    #             else:
    #                 button = types.InlineKeyboardButton(text=i[0], callback_data=f"settings_{i[1]}")
    #                 keys[f'but{index}'] = button
    #
    #             if len(keys_list) == 8:
    #                 if index == 0 or index == 5:
    #                     keyboard_list.append([button])
    #                 elif index == 2 or index == 4 or index == 7:
    #                     previous_button = keys[f'but{index - 1}']
    #                     keyboard_list.append([previous_button, button])
    #                 else:
    #                     pass
    #             else:
    #                 if index == 0 or index >= 5:
    #                     keyboard_list.append([button])
    #                 elif index == 2 or index == 4:
    #                     previous_button = keys[f'but{index - 1}']
    #                     keyboard_list.append([previous_button, button])
    #                 else:
    #                     pass
    #         back_value_button = types.InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data=self.back_value)
    #         keyboard_list.append([back_value_button])
    #         kb2 = types.InlineKeyboardMarkup(inline_keyboard=keyboard_list, resize_keyboard=True)
    #         await asyncio.sleep(0.3)
    #         await self.bot.edit_message_text(text=f'Выбраны следующие склады: {", ".join(self.keyboard_dict)}\n\n'
    #                                          f'Настройте необходимые параметры:', chat_id=self.message.chat.id,
    #                                          message_id=self.message.message_id)
    #         await self.bot.edit_message_reply_markup(chat_id=self.message.chat.id, message_id=self.message.message_id,
    #                                                  reply_markup=kb2)
    #
    # async def scheduler_block_menu_buttons(self):
    #     kb_schedulers_menu = InlineKeyboardMarkup(inline_keyboard=[
    #         [InlineKeyboardButton(
    #             text='🔴🗞 Отправка новостей' if sheduler_block_value.news is False else '🟢🗞 Отправка новостей',
    #             callback_data='scheduler_news_false' if sheduler_block_value.news is False else
    #             'scheduler_news_true')],
    #         [InlineKeyboardButton(
    #             text='️🔴💰 Отправка кэфов приемки' if sheduler_block_value.warehouses is False else '️🟢💰 Отправка кэфов '
    #                                                                                               'приемки',
    #             callback_data='scheduler_warehouses_false' if sheduler_block_value.warehouses is False else
    #             'scheduler_warehouses_true')],
    #         [InlineKeyboardButton(text='🔙 Вернуться назад', callback_data='func_menu')]
    #     ])
    #     await self.bot.edit_message_reply_markup(chat_id=self.message.chat.id, message_id=self.message.message_id,
    #                                              reply_markup=kb_schedulers_menu)
