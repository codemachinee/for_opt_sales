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

from FSM import Another_model, Message_from_admin, Next_level_base, Rassylka
from functions import admin_account, clients_base
from keyboards import Buttons, kb_price, kb_price_two
from configs.passwords import loggs_acc

moscow_tz = pytz.timezone("Europe/Moscow")

async def start(message: Message, bot, state: FSMContext):
    await state.clear()
    try:
        if message.chat.id == admin_account.admin:
            start_file = FSInputFile(r'start_logo.png', 'rb')
            await bot.send_photo(message.chat.id, start_file, caption='Здравствуйте! Вас приветствует autoallure.dmd_bot - '
                                                                      'надежный сервис и помощник по уходу за Вашим '
                                                                      'автомобилем.🚘\n\n'
                                                                      '/price - расчет цены на услуги autoallure для '
                                                                      'Вашего авто\n/help - все возможности бота\n\n'
                                                                      'режим: Администратор')

        else:
            data_from_database = await db.search_in_table(message.chat.id)
            if data_from_database is not False and data_from_database[1][0][4] >= 8:
                pass
            else:
                start_file = FSInputFile(r'start_logo.png', 'rb')
                await bot.send_photo(message.chat.id, start_file,
                                     caption='Здравствуйте! Вас приветствует autoallure.dmd_bot - '
                                             'надежный сервис и помощник по уходу за Вашим '
                                             'автомобилем.🚘\n\n'
                                             '/price - расчет цены на услуги autoallure для '
                                             'Вашего авто\n/help - все возможности бота\n\n'
                                             '@hlapps - разработка ботов любой сложности')
    except Exception as e:
        logger.exception('Ошибка в handlers/start', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/start: {e}')


async def help(message: Message, bot, state: FSMContext):
    await state.clear()
    if message.chat.id == admin_account.admin:      # условия демонстрации различных команд для админа и клиентов
        await bot.send_message(message.chat.id, 'Основные команды поддерживаемые ботом:\n'
                                                     '/price -  расчет услуг для любого авто\n'
                                                     '/start - инициализация бота\n'
                                                     '/help - справка по боту\n'
                                                     '/post - устроить рассылку\n'
                                                     '/next_level_base - перевод клиента из базы "потенциальные клиенты" в базу '
                                                     '"старые клиенты"\n'
                                                     '/sent_message -  отправка через бота сообщения клиенту по id чата\n'
                                                     '/result - посмотреть на отзывы и галерею с результатом работ\n'
                                                     '/day_visitors - пользователи посетившие бота сегодня\n'
                                                     '/reset_cash - сбросить кэш базы данных')

    else:
        data_from_database = await db.search_in_table(message.chat.id)
        if data_from_database is not False and data_from_database[1][0][4] >= 8:
            pass
        else:
            await bot.send_message(message.chat.id, 'Основные команды поддерживаемые ботом:\n'
                                                         '/price -  расчет услуг для любого авто\n'
                                                         '/start - инициализация бота\n'
                                                         '/help - справка по боту\n'
                                                         '/result - посмотреть на отзывы и галерею с результатом работ\n\n\n'
                                                    '@hlapps - разработка ботов любой сложности')


async def sent_message(message: Message, bot, state: FSMContext):
    try:
        await state.clear()
        if message.chat.id == admin_account.admin:
            await bot.send_message(admin_account.admin, 'Введи id чата клиента, которому нужно написать от лица бота')
            await state.set_state(Message_from_admin.user_id)
        else:
            await bot.send_message(message.chat.id, 'У Вас нет прав для использования данной команды')
    except Exception as e:
        logger.exception('Ошибка в handlers/sent_message', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/sent_message: {e}')


async def post(message: Message, bot, state: FSMContext):
    await state.clear()
    try:
        if message.chat.id == admin_account.admin:
            await Buttons(bot, message).rasylka_buttons()
            await state.set_state(Rassylka.post)

        else:
            await bot.send_message(message.chat.id, 'У Вас нет прав для использования данной команды')
    except Exception as e:
        logger.exception('Ошибка в handlers/post', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/post {e}')


async def reset_cash(message: Message, bot, state: FSMContext):
    await state.clear()
    try:
        if message.chat.id == admin_account.admin:
            await db.delete_all_users()
            await bot.send_message(message.chat.id, 'Кэш очищен',
                                   message_thread_id=message.message_thread_id)
        else:
            await bot.send_message(message.chat.id, 'Недостаточно прав',
                                   message_thread_id=message.message_thread_id)
    except Exception as e:
        logger.exception('Ошибка в handlers/reset_cashe', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/reset_cash: {e}')


async def day_visitors(message: Message, bot, state: FSMContext):
    await state.clear()
    try:
        if message.chat.id == admin_account.admin:
            data = await db.return_base_data()
            if data is False:
                await bot.send_message(message.chat.id, 'Сегодня пользователей не было')
            else:
                table_header = f"Пользователи воспользовавшиеся ботом сегодня {len(data)}:\n\n"
                table_body = " *Telegram ID* | *Ссылка* | *Имя* | *Время* | *Ход*\n"
                table_body += "-" * 44 + "\n"
                for i in data:
                    table_body += f"{i[0]} | @{i[1]} | {i[2]} | {i[3][11:16]} | {i[4]}\n" + ("-" * 44 + "\n")

                await bot.send_message(message.chat.id, table_header + table_body, parse_mode="Markdown")
        else:
            await bot.send_message(message.chat.id, 'Недостаточно прав',
                                   message_thread_id=message.message_thread_id)
    except Exception as e:
        logger.exception('Ошибка в handlers/day_visitors', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/day_visitors: {e}')


async def check_callbacks(callback: CallbackQuery, bot, state: FSMContext):
    assert callback.message is not None   # обозначаем для проверочной библиотеки mypy, чтобы избегать лишних ошибок при тесте
    assert callback.data is not None
    data_from_database = await db.search_in_table(callback.message.chat.id)
    if callback.message.chat.id != admin_account.admin:
        if data_from_database is not False:
            if data_from_database[1][0][4] >= 8:
                return
            else:
                await db.update_table(telegram_id=callback.message.chat.id, update_dates=datetime.now(moscow_tz))
        else:
            await db.add_user(update_telegram_id=callback.message.chat.id, update_username=callback.from_user.username,
                              update_name=callback.from_user.first_name, update_dates=datetime.now(moscow_tz))
            data_from_database = [True, [[callback.message.chat.id, callback.from_user.username, callback.from_user.first_name,
                                          datetime.now(), 1]]]
    try:
        async with aiofiles.open('price.json', "r", encoding="utf-8") as file:
            content = await file.read()
            data = json.loads(content)
            if callback.data == 'page_one':
                await Buttons(bot, callback.message).marka_buttons(next_button='page_two', back_button=None)
            elif callback.data == 'page_two':
                await Buttons(bot, callback.message).marka_buttons(next_button=None, back_button='page_one')
            elif callback.data == 'zayavka_yes':
                if callback.message.chat.id == admin_account.admin:
                    await bot.send_message(admin_account.admin, 'не доступно для админа')
                elif callback.from_user.username is not None:
                    await bot.edit_message_text(text='Заявка оформлена и передана мастеру, с Вами свяжутся в ближайшее время. '
                                                'Спасибо, что выбрали нас.🤝\n\n'
                                                'Если желаете сообщить что-то дополнительно, отправьте в сообщении 💬\n'
                                                'Для нового расчета воспользуйтесь командой /price',
                                                chat_id=callback.message.chat.id, message_id=callback.message.message_id)
                    await bot.send_message(admin_account.admin, f'🚨!!!СРОЧНО!!!🚨\n'
                                                    f'Хозяин, поступила ЗАЯВКА от:\n'
                                                    f'Псевдоним: @{callback.from_user.username}\n'
                                                    f'id чата: {callback.message.chat.id}\n'
                                                    f'Быстрее согласуй дату и закрой заявку пока он не слился'
                                                    f'\n'
                                                    f'В случае положительной отработки заявки не забудь перевести клиента из базы '
                                                    f'"потенциальные клиенты" в базу "старые клиенты" с помощью команды\n '
                                                    f'/next_level_base\n'
                                                    f'/sent_message - отправить сообщение с помощью бота')
                else:
                    await bot.send_message(callback.message.chat.id, 'Заявка оформлена и передана мастеру, пожалуйста перейдите в чат '
                                                      '@pogonin21 и напишите любое сообщение или отправьте в ответ на это '
                                                      'сообщение свой номер телефона в любом формате. '
                                                      'Спасибо, что выбрали нас.🤝\n'
                                                      'Для нового расчета воспользуйтесь командой /price')
                    await bot.send_message(admin_account.admin, f'🚨!!!СРОЧНО!!!🚨\n'
                                                    f'Хозяин, поступила ЗАЯВКА от:\n'
                                                    f'Псевдоним: @{callback.from_user.username}\n'
                                                    f'id чата: {callback.message.chat.id}\n'
                                                    f'Быстрее согласуй дату и закрой заявку пока он не слился\n'
                                                    f'В случае положительной отработки заявки не забудь перевести клиента из базы '
                                                    f'"потенциальные клиенты" в базу "старые клиенты" с помощью команды\n '
                                                    f'/next_level_base\n'
                                                    f'/sent_message - отправить сообщение с помощью бота')
                await state.set_state(Another_model.message)
            elif callback.data in list(data.keys()):
                await state.update_data(marka=callback.data)
                await Buttons(bot, callback.message).models_buttons(callback.data)
            elif callback.data == 'price_menu':
                if callback.message.reply_markup == kb_price:
                    pass
                else:
                    await bot.edit_message_text(chat_id=callback.message.chat.id, text='Пожалуйста выберите марку Вашего '
                                                                                       'автомобиля 🚐:',
                                                message_id=callback.message.message_id, reply_markup=kb_price)
            elif callback.data == 'price_menu_two':
                if callback.message.reply_markup == kb_price_two:
                    pass
                else:
                    await bot.edit_message_text(chat_id=callback.message.chat.id, text='Пожалуйста выберите марку Вашего '
                                                                                       'автомобиля 🚐:',
                                                message_id=callback.message.message_id, reply_markup=kb_price_two)
            elif callback.data.startswith('another_'):
                kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="↩️ Вернуться",
                                                                                 callback_data=callback.data[8:])]])
                await state.update_data(marka=callback.data[8:])
                await bot.edit_message_text(chat_id=callback.message.chat.id, text='Пожалуйста введите марку Вашего '
                                                                                   'автомобиля ⌨️:',
                                            message_id=callback.message.message_id, reply_markup=kb)
                await state.set_state(Another_model.model)
            elif callback.data.endswith('_class'):
                mes = await bot.edit_message_text(text='загрузка..🚀', chat_id=callback.message.chat.id,
                                                  message_id=callback.message.message_id)
                if callback.message.chat.id != admin_account.admin:
                    if data_from_database[1][0][4] >= 6:
                        await bot.edit_message_text(chat_id=callback.message.chat.id,
                                                    text='Превышен дневной лимит обращений.',
                                                    message_id=callback.message.message_id)
                        await db.update_table(telegram_id=callback.message.chat.id, update_dates=datetime.now(moscow_tz),
                                              update_number_of_requests=data_from_database[1][0][4] + 1)
                        return
                    else:
                        await db.update_table(telegram_id=callback.message.chat.id, update_dates=datetime.now(moscow_tz),
                                              update_number_of_requests=data_from_database[1][0][4] + 1)
                data = await state.get_data()
                data_marka = data.get('marka')
                file_open = FSInputFile(f'{callback.data}.png', 'rb')
                media = InputMediaPhoto(media=file_open, caption=f'Готово!\n'
                                                                 f'Стоимость услуг для Вашего автомобиля {data_marka}\n'
                                                                 f'соответствует {callback.data[0]} ценовому классу.\n'
                                                                 f'/help - справка по боту \n'
                                                                 f'/result - посмотреть на отзывы и результат работ')
                await bot.edit_message_media(media=media, chat_id=callback.message.chat.id, message_id=mes.message_id)
                await Buttons(bot, callback.message).zayavka_buttons(data_marka)
                if callback.message.chat.id != admin_account.admin and data_from_database[1][0][4] < 2:
                    await bot.send_message(admin_account.admin, f'Хозяин! Замечена активность:\n'
                                                          f'Имя: {callback.from_user.first_name}\n'
                                                          f'Фамилия: {callback.from_user.last_name}\n'
                                                          f'Никнейм: {callback.from_user.username}\n'
                                                          f'Ссылка: @{callback.from_user.username}\n'
                                                          f'Авто: {data_marka} {callback.data[0]} класса')
                    await clients_base(bot, callback.message, auto_model=f'{data_marka} {callback.data[0]} класса').chec_and_record()
                else:
                    return
            elif callback.data == 'Общая база клиентов':
                await bot.edit_message_text(text='База для рассылки: Общая база клиентов\nОтправь мне пост 💬',
                                            chat_id=admin_account.admin, message_id=callback.message.message_id)
                await state.update_data(base=callback.data)
                await state.set_state(Rassylka.post)
            elif callback.data == 'База потенциальных клиентов':
                await bot.edit_message_text(text='База для рассылки: ️База потенциальных клиентов\nОтправь мне пост 💬',
                                            chat_id=admin_account.admin, message_id=callback.message.message_id)
                await state.update_data(base=callback.data)
                await state.set_state(Rassylka.post)
            elif callback.data == 'База старых клиентов':
                await bot.edit_message_text(text='База для рассылки: ️База старых клиентов\nОтправь мне пост 💬',
                                            chat_id=admin_account.admin, message_id=callback.message.message_id)
                await state.update_data(base=callback.data)
                await state.set_state(Rassylka.post)
    except Exception as e:
        logger.exception('Ошибка в handlers/check_callbacks', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/check_callbacks: {e}')



