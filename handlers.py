import json
from datetime import datetime

import aiofiles
import pytz
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
    ReplyKeyboardRemove,
)
from loguru import logger

from FSM import Get_admin, Rassylka, Message_from_admin, Next_level_base
from configs.passwords import admins_list, group_id
from functions import antispam
from structure import structure_menu

# from FSM import Another_model, Message_from_admin, Next_level_base, Rassylka
from functions import clients_base, is_today

from keyboards import Buttons, kb_main_menu
from configs.passwords import loggs_acc
from redis_file import redis_storage

moscow_tz = pytz.timezone("Europe/Moscow")

async def start(message: Message, bot, state: FSMContext):
    await state.clear()
    try:
        if message.chat.id in admins_list:
            await bot.send_message(message.chat.id, '<b>Бот-поддержки оптовых продаж из 🇨🇳 инициализирован.</b>\n'
                                                    '<b>Режим доступа</b>: Администратор\n'
                                                    '/help - справка по боту',
                                   message_thread_id=message.message_thread_id,
                                   parse_mode='html')
            await Buttons(bot, message, structure_menu["Основное меню"]).new_main_menu_buttons()
        elif await antispam(bot, message) is False:
                pass
        else:
            await bot.send_message(message.chat.id, '<b>Бот-поддержки оптовых продаж из 🇨🇳 инициализирован.</b>\n'
                                                    '/help - справка по боту',
                                   message_thread_id=message.message_thread_id,
                                   parse_mode='html')
            await Buttons(bot, message, structure_menu["Основное меню"]).new_main_menu_buttons()
    except Exception as e:
        logger.exception('Ошибка в handlers/start', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/start: {e}')


async def help(message: Message, bot, state: FSMContext):
    await state.clear()
    if message.chat.id in admins_list:      # условия демонстрации различных команд для админа и клиентов
        await bot.send_message(message.chat.id, 'Основные команды поддерживаемые ботом:\n'
                                                     '/menu - главное функциональное меню\n'
                                                     '/start - инициализация бота\n'
                                                     '/help - справка по боту\n'
                                                     '/post - устроить рассылку\n'
                                                     '/sent_message -  отправка через бота сообщения клиенту по id чата\n'
                                                     '/day_visitors - пользователи посетившие бота сегодня\n'
                                                     '/reset_cash - сбросить кэш базы данных')

    elif await antispam(bot, message) is False:
        pass

    else:
        await bot.send_message(message.chat.id, 'Основные команды поддерживаемые ботом:\n'
                                                     '/menu - главное функциональное меню\n'
                                                     '/start - инициализация бота\n'
                                                     '/help - справка по боту\n\n\n'
                                                '@hlapps - разработка ботов любой сложности')


async def menu(message: Message, bot, state: FSMContext):
    await state.clear()
    if message.chat.id in admins_list:  # условия демонстрации различных команд для админа и клиентов
        await Buttons(bot, message, structure_menu["Основное меню"]).new_main_menu_buttons()
    elif await antispam(bot, message) is False:
        pass

    else:
        await Buttons(bot, message, structure_menu["Основное меню"]).new_main_menu_buttons()


async def reset_cash(message: Message, bot, state: FSMContext):
    try:
        await state.clear()
        if message.chat.id in admins_list:
            await redis_storage.clear()
            await bot.send_message(message.chat.id, 'Кэш очищен', message_thread_id=message.message_thread_id)
        else:
            await bot.send_message(message.chat.id, 'У Вас нет прав для использования данной команды')
    except Exception as e:
        logger.exception('Ошибка в handlers/sent_message', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/sent_message: {e}')


async def post(message: Message, bot, state: FSMContext):
    await state.clear()
    try:
        if message.chat.id in admins_list:
            await Buttons(bot, message, {}).rasylka_buttons()
            await state.set_state(Rassylka.post)

        else:
            await bot.send_message(message.chat.id, 'У Вас нет прав для использования данной команды')
    except Exception as e:
        logger.exception('Ошибка в handlers/post', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/post {e}')


async def sent_message(message: Message, bot, state: FSMContext):
    try:
        await state.clear()
        if message.chat.id in admins_list:
            await bot.send_message(message.chat.id, 'Введи id чата клиента, которому нужно написать от лица бота')
            await state.set_state(Message_from_admin.user_id)
        else:
            await bot.send_message(message.chat.id, 'У Вас нет прав для использования данной команды')
    except Exception as e:
        logger.exception('Ошибка в handlers/sent_message', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/sent_message: {e}')


async def day_visitors(message: Message, bot, state: FSMContext):
    await state.clear()
    today_list = []
    mess = await bot.send_message(message.chat.id, 'загрузка..🚀')
    try:
        if message.chat.id in admins_list:
            data = await clients_base.get_clients()
            for d in data:
                if  await is_today(data[d]["date"]) is True:
                    step = await redis_storage.get(d)
                    if step is None:
                        step = 0
                    today_list.append([d, data[d]["username"], data[d]["name"], data[d]["date"], step])
                else:
                    pass

            if len(today_list) == 0:
                await bot.edit_message_text(chat_id=message.chat.id, text='Сегодня пользователей не было', message_id=mess.message_id)
            else:
                table_header = f"Пользователи воспользовавшиеся ботом сегодня {len(today_list)}:\n\n"
                table_body = " *Telegram ID* | *Ссылка* | *Имя* | *Время* | *Ход*\n"
                table_body += "-" * 44 + "\n"
                for i in today_list:
                    table_body += f"{i[0]} | @{i[1]} | {i[2]} | {i[3][9:]} | {i[4]}\n" + ("-" * 44 + "\n")

                await bot.edit_message_text(chat_id=message.chat.id, text=table_header+table_body,
                                            message_id=mess.message_id, parse_mode="Markdown")
        else:
            await bot.send_message(message.chat.id, 'Недостаточно прав',
                                   message_thread_id=message.message_thread_id)
    except Exception as e:
        logger.exception('Ошибка в handlers/day_visitors', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/day_visitors: {e}')


async def check_callbacks(callback: CallbackQuery, bot, state: FSMContext):
    assert callback.message is not None   # обозначаем для проверочной библиотеки mypy, чтобы избегать лишних ошибок при тесте
    assert callback.data is not None
    if callback.message.chat.id not in admins_list:
        antispam_answer = await antispam(bot, callback.message)
        if antispam_answer is False:
            return

        elif antispam_answer == "Предупреждение":
            await bot.edit_message_text(chat_id=callback.message.chat.id,
                                        text='Превышен дневной лимит обращений.',
                                        message_id=callback.message.message_id)
            return
    try:
        if callback.data == "📋 Каталоги товаров и цен":
            await bot.send_message(callback.message.chat.id, 'Каталог сетевых фильтров: '
                                                             'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                                                             'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing')

        elif callback.data == "🚚 Вопросы по логистике":
            await Buttons(bot, callback.message, {},"Основное меню", "⚙️ Фрагмент в разработке").menu_buttons()

        elif callback.data == "💰 Вопросы по оплате":
            await Buttons(bot, callback.message, {},"Основное меню", "⚙️ Фрагмент в разработке").menu_buttons()

        elif callback.data == "👨🏻‍💻 Чат с администратором":
            await bot.edit_message_text(chat_id=callback.message.chat.id,
                                   text='Информация передана администратору, с Вами скоро свяжутся. '
                                        'Если желаете сообщить что-то дополнительно, отправьте в сообщении 💬\n'
                                        'Спасибо, что выбрали нас.🤝\n'
                                        'Для возвращения меню: /menu', message_id=callback.message.message_id)

            await bot.send_message(group_id, f'🚨!!!СРОЧНО!!!🚨\n'
                                            f'поступил запрос на ЧАТ С АДМИНИСТРАТОРОМ от:\n'
                                            f'Ссылка: @{callback.from_user.username}\n'
                                            f'id чата: {callback.message.chat.id}\n'
                                            f'Если ссылка на чат отсутствует запроси контакт или отправь свой с помощью команды:\n'
                                            f'/sent_message - отправить сообщение с помощью бота')
            await state.set_state(Get_admin.message)

        elif callback.data == "ℹ️ О нас":
            await Buttons(bot, callback.message, {},"Основное меню", "⚙️ Фрагмент в разработке").menu_buttons()

        elif callback.data == "Основное меню":
            await Buttons(bot, callback.message, structure_menu["Основное меню"], menu_level= "Пожалуйста выберите интересующий пункт меню:").menu_buttons()

        elif callback.data == "📦 Закупка оптом":
            await Buttons(bot, callback.message, structure_menu["Основное меню"]["📦 Закупка оптом"],
                          back_button="Основное меню",
                          menu_level= "Пожалуйста выберите категорию товаров:").menu_buttons()
            await state.set_state(Next_level_base.kategoriya)

        elif callback.data in structure_menu["Основное меню"]["📦 Закупка оптом"]:
            await Buttons(bot, callback.message, structure_menu["Основное меню"]["📦 Закупка оптом"][f'{callback.data}'],
                          back_button="📦 Закупка оптом", kategoriya= f'{callback.data}__',
                          menu_level= "Пожалуйста выберите бренд:").menu_buttons()
            await state.set_state(Next_level_base.brand)

        elif '__' in callback.data:
            split_list = callback.data.split('__')
            await Buttons(bot, callback.message,
                          structure_menu["Основное меню"]["📦 Закупка оптом"][f'{split_list[0]}'][f'{split_list[1]}'],
                          back_button=f'{split_list[0]}',
                          menu_level="Пожалуйста выберите модель/серию:").menu_buttons()
        # elif callback.data == 'page_two':
        #     await Buttons(bot, callback.message).marka_buttons(next_button=None, back_button='page_one')
        # elif callback.data == 'zayavka_yes':
        #     if callback.message.chat.id == admin_account.admin:
        #         await bot.send_message(admin_account.admin, 'не доступно для админа')
        #     elif callback.from_user.username is not None:
        #         await bot.edit_message_text(text='Заявка оформлена и передана мастеру, с Вами свяжутся в ближайшее время. '
        #                                     'Спасибо, что выбрали нас.🤝\n\n'
        #                                     'Если желаете сообщить что-то дополнительно, отправьте в сообщении 💬\n'
        #                                     'Для нового расчета воспользуйтесь командой /price',
        #                                     chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        #         await bot.send_message(admin_account.admin, f'🚨!!!СРОЧНО!!!🚨\n'
        #                                         f'Хозяин, поступила ЗАЯВКА от:\n'
        #                                         f'Псевдоним: @{callback.from_user.username}\n'
        #                                         f'id чата: {callback.message.chat.id}\n'
        #                                         f'Быстрее согласуй дату и закрой заявку пока он не слился'
        #                                         f'\n'
        #                                         f'В случае положительной отработки заявки не забудь перевести клиента из базы '
        #                                         f'"потенциальные клиенты" в базу "старые клиенты" с помощью команды\n '
        #                                         f'/next_level_base\n'
        #                                         f'/sent_message - отправить сообщение с помощью бота')
        #     else:
        #         await bot.send_message(callback.message.chat.id, 'Заявка оформлена и передана мастеру, пожалуйста перейдите в чат '
        #                                           '@pogonin21 и напишите любое сообщение или отправьте в ответ на это '
        #                                           'сообщение свой номер телефона в любом формате. '
        #                                           'Спасибо, что выбрали нас.🤝\n'
        #                                           'Для нового расчета воспользуйтесь командой /price')
        #         await bot.send_message(admin_account.admin, f'🚨!!!СРОЧНО!!!🚨\n'
        #                                         f'Хозяин, поступила ЗАЯВКА от:\n'
        #                                         f'Псевдоним: @{callback.from_user.username}\n'
        #                                         f'id чата: {callback.message.chat.id}\n'
        #                                         f'Быстрее согласуй дату и закрой заявку пока он не слился\n'
        #                                         f'В случае положительной отработки заявки не забудь перевести клиента из базы '
        #                                         f'"потенциальные клиенты" в базу "старые клиенты" с помощью команды\n '
        #                                         f'/next_level_base\n'
        #                                         f'/sent_message - отправить сообщение с помощью бота')
        #     await state.set_state(Another_model.message)
        # elif callback.data in list(data.keys()):
        #     await state.update_data(marka=callback.data)
        #     await Buttons(bot, callback.message).models_buttons(callback.data)
        # elif callback.data == 'price_menu':
        #     if callback.message.reply_markup == kb_price:
        #         pass
        #     else:
        #         await bot.edit_message_text(chat_id=callback.message.chat.id, text='Пожалуйста выберите марку Вашего '
        #                                                                            'автомобиля 🚐:',
        #                                     message_id=callback.message.message_id, reply_markup=kb_price)
        # elif callback.data == 'price_menu_two':
        #     if callback.message.reply_markup == kb_price_two:
        #         pass
        #     else:
        #         await bot.edit_message_text(chat_id=callback.message.chat.id, text='Пожалуйста выберите марку Вашего '
        #                                                                            'автомобиля 🚐:',
        #                                     message_id=callback.message.message_id, reply_markup=kb_price_two)
        # elif callback.data.startswith('another_'):
        #     kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="↩️ Вернуться",
        #                                                                      callback_data=callback.data[8:])]])
        #     await state.update_data(marka=callback.data[8:])
        #     await bot.edit_message_text(chat_id=callback.message.chat.id, text='Пожалуйста введите марку Вашего '
        #                                                                        'автомобиля ⌨️:',
        #                                 message_id=callback.message.message_id, reply_markup=kb)
        #     await state.set_state(Another_model.model)
        # elif callback.data.endswith('_class'):
        #     mes = await bot.edit_message_text(text='загрузка..🚀', chat_id=callback.message.chat.id,
        #                                       message_id=callback.message.message_id)
        #     if callback.message.chat.id != admin_account.admin:
        #         if data_from_database[1][0][4] >= 6:
        #             await bot.edit_message_text(chat_id=callback.message.chat.id,
        #                                         text='Превышен дневной лимит обращений.',
        #                                         message_id=callback.message.message_id)
        #             await db.update_table(telegram_id=callback.message.chat.id, update_dates=datetime.now(moscow_tz),
        #                                   update_number_of_requests=data_from_database[1][0][4] + 1)
        #             return
        #         else:
        #             await db.update_table(telegram_id=callback.message.chat.id, update_dates=datetime.now(moscow_tz),
        #                                   update_number_of_requests=data_from_database[1][0][4] + 1)
        #     data = await state.get_data()
        #     data_marka = data.get('marka')
        #     file_open = FSInputFile(f'{callback.data}.png', 'rb')
        #     media = InputMediaPhoto(media=file_open, caption=f'Готово!\n'
        #                                                      f'Стоимость услуг для Вашего автомобиля {data_marka}\n'
        #                                                      f'соответствует {callback.data[0]} ценовому классу.\n'
        #                                                      f'/help - справка по боту \n'
        #                                                      f'/result - посмотреть на отзывы и результат работ')
        #     await bot.edit_message_media(media=media, chat_id=callback.message.chat.id, message_id=mes.message_id)
        #     await Buttons(bot, callback.message).zayavka_buttons(data_marka)
        #     if callback.message.chat.id != admin_account.admin and data_from_database[1][0][4] < 2:
        #         await bot.send_message(admin_account.admin, f'Хозяин! Замечена активность:\n'
        #                                               f'Имя: {callback.from_user.first_name}\n'
        #                                               f'Фамилия: {callback.from_user.last_name}\n'
        #                                               f'Никнейм: {callback.from_user.username}\n'
        #                                               f'Ссылка: @{callback.from_user.username}\n'
        #                                               f'Авто: {data_marka} {callback.data[0]} класса')
        #         await clients_base(bot, callback.message, auto_model=f'{data_marka} {callback.data[0]} класса').chec_and_record()
        #     else:
        #         return
        elif callback.data == 'Общая база клиентов':
            await bot.edit_message_text(text='База для рассылки: Общая база клиентов\nОтправь мне пост 💬',
                                        chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            await state.update_data(base=callback.data)
            await state.set_state(Rassylka.post)
        # elif callback.data == 'База потенциальных клиентов':
        #     await bot.edit_message_text(text='База для рассылки: ️База потенциальных клиентов\nОтправь мне пост 💬',
        #                                 chat_id=admin_account.admin, message_id=callback.message.message_id)
        #     await state.update_data(base=callback.data)
        #     await state.set_state(Rassylka.post)
        # elif callback.data == 'База старых клиентов':
        #     await bot.edit_message_text(text='База для рассылки: ️База старых клиентов\nОтправь мне пост 💬',
        #                                 chat_id=admin_account.admin, message_id=callback.message.message_id)
        #     await state.update_data(base=callback.data)
        #     await state.set_state(Rassylka.post)
    except Exception as e:
        logger.exception('Ошибка в handlers/check_callbacks', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/check_callbacks: {e}')



