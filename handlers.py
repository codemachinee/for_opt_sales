import asyncio

import pytz
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from assistent import assistant_manager
from configs.passwords import admins_list, group_id, loggs_acc
from FSM import Get_admin, Message_from_admin, Next_level_base, Rassylka
from functions import antispam, clients_base, is_today
from keyboards import Buttons
from redis_file import redis_storage
from structure import HELP_TEXT, structure_menu

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
            await Buttons(bot, message, structure_menu["Основное меню"],
                          menu_level='Пожалуйста выберите интересующий пункт меню:').new_main_menu_buttons()
        elif await antispam(bot, message) is False:
                pass
        else:
            await bot.send_message(message.chat.id, '<b>Бот-поддержки оптовых продаж из 🇨🇳 инициализирован.</b>\n'
                                                    '/help - справка по боту',
                                   message_thread_id=message.message_thread_id,
                                   parse_mode='html')
            await Buttons(bot, message, structure_menu["Основное меню"],
                          menu_level='Пожалуйста выберите интересующий пункт меню:').new_main_menu_buttons()
    except Exception as e:
        logger.exception('Ошибка в handlers/start', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/start: {e}')


async def help(message: Message, bot, state: FSMContext):
    await state.clear()
    if message.chat.id in admins_list:      # условия демонстрации различных команд для админа и клиентов
        await bot.send_message(message.chat.id, '<b>Основные команды поддерживаемые ботом:\n</b>'
                                                     '/menu - главное функциональное меню\n'
                                                     '/start - инициализация бота\n'
                                                     '/help - список доступных команд\n'
                                                     '/post - устроить рассылку\n'
                                                     '/sent_message -  отправка через бота сообщения клиенту по id чата\n'
                                                     '/day_visitors - пользователи посетившие бота сегодня\n'
                                                     '/reload_assistant - перезагрузка ассистента\n'
                                                     '/reset_cash - сбросить кэш базы данных',  parse_mode='html')

    elif await antispam(bot, message) is False:
        pass

    else:
        await bot.send_message(message.chat.id, '<b>Основные команды поддерживаемые ботом:\n</b>'
                                                     '/menu - главное функциональное меню\n'
                                                     '/start - инициализация бота\n'
                                                     '/help - список доступных команд\n\n\n'
                                                '@hlapps - разработка ботов любой сложности',  parse_mode='html')


async def menu(message: Message, bot, state: FSMContext):
    await state.clear()
    if message.chat.id in admins_list:  # условия демонстрации различных команд для админа и клиентов
        await Buttons(bot, message, structure_menu["Основное меню"],
                      menu_level='Пожалуйста выберите интересующий пункт меню:').new_main_menu_buttons()
    elif await antispam(bot, message) is False:
        pass

    else:
        await Buttons(bot, message, structure_menu["Основное меню"],
                      menu_level='Пожалуйста выберите интересующий пункт меню:').new_main_menu_buttons()


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


# async def reload_assistant(message: Message, bot, state: FSMContext):
#     try:
#         await state.clear()
#         if message.chat.id in admins_list:
#             await assistant_manager.manual_reload()
#             await message.answer("Ассистент успешно перезагружен.")
#         else:
#             await bot.send_message(message.chat.id, 'У Вас нет прав для использования данной команды')
#     except Exception as e:
#         logger.exception('Ошибка в handlers/reload_assistant', e)
#         await bot.send_message(loggs_acc, f'Ошибка в handlers/reload_assistant: {e}')


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
            await bot.send_message(callback.message.chat.id, '<b>Каталог сетевых фильтров: </b>'
                                                             'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                                                             'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing',
                                   parse_mode='html')
            await asyncio.sleep(0.2)
            await bot.send_message(callback.message.chat.id, '<b>Каталог OTG/Хабы/кардридеры: </b>'
                                   'https://docs.google.com/spreadsheets/d/1ZmC3cxYSyupkvNyevNKkpt4LiFniypUH/'
                                   'edit?usp=sharing&ouid=117298760559545275811&rtpof=true&sd=true', parse_mode='html')
            await asyncio.sleep(0.2)
            await bot.send_message(callback.message.chat.id, '<b>Каталог беспроводных наушников: </b>'
                                                             'https://docs.google.com/spreadsheets/d/1lc1tBWMCSOGKwdM-'
                                                             'U6C7U1R3lRJLsUX99FCVAsaax5E/edit?usp=sharing',
                                   parse_mode='html')
            await asyncio.sleep(0.2)
            await bot.send_message(callback.message.chat.id, '<b>Каталог держателей/подставок устройств: </b>'
                                                             'https://docs.google.com/spreadsheets/d/1p4xQXqozQugy3N'
                                                             'aHut3TUY6COqvzCgYb2AEMV1Cx6Zc/edit?usp=sharing',
                                   parse_mode='html')
            await asyncio.sleep(0.2)
            await bot.send_message(callback.message.chat.id, '<b>Каталог Powerbanks/станции питания(BAVIN):</b> ',
                                   'https://docs.google.com/spreadsheets/d/1ZmC3cxYSyupkvNyevNKkpt4LiFniypUH/'
                                   'edit?usp=sharing&ouid=117298760559545275811&rtpof=true&sd=true', parse_mode='html')

        elif callback.data == "🚚 Вопросы по логистике":
            await Buttons(bot, callback.message, {},"Основное меню", menu_level="⚙️ Фрагмент в разработке").menu_buttons()

        elif callback.data == "💰 Вопросы по оплате":
            await Buttons(bot, callback.message, {},"Основное меню", menu_level="⚙️ Фрагмент в разработке").menu_buttons()

        elif callback.data == "❓ Как пользоваться":
            await Buttons(bot, callback.message, {},"Основное меню",
                          menu_level=HELP_TEXT).menu_buttons()

        elif callback.data == "👨🏻‍💻 Чат с администратором":
            await bot.edit_message_text(chat_id=callback.message.chat.id,
                                   text='Информация передана администратору, с Вами скоро свяжутся. '
                                        'Если желаете сообщить что-то дополнительно, отправьте в сообщении 💬\n'
                                        'Спасибо, что выбрали нас.🤝\n'
                                        'Для возвращения меню: /menu', message_id=callback.message.message_id)

            await bot.send_message(group_id, f'🚨!!!СРОЧНО!!!🚨\n'
                                            f'<b>поступил запрос на ЧАТ С АДМИНИСТРАТОРОМ от:</b>\n'
                                            f'Ссылка: @{callback.from_user.username}\n'
                                            f'id чата: {callback.message.chat.id}\n'
                                            f'<b>Если ссылка на чат отсутствует запроси контакт или отправь свой с помощью команды</b>:\n'
                                            f'/sent_message - отправить сообщение с помощью бота', parse_mode="html")
            await state.set_state(Get_admin.message)

        elif callback.data == "ℹ️ О нас":
            await Buttons(bot, callback.message, {},"Основное меню", menu_level="⚙️ Фрагмент в разработке").menu_buttons()

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
            await state.update_data(kategoriya=callback.data)
            await state.set_state(Next_level_base.brand)

        elif '__' in callback.data:
            split_list = callback.data.split('__')
            if split_list[1].startswith("💰 "):
                if split_list[1] == "💰 Каталог(Проекторы)":
                    await Buttons(bot, callback.message, {}, "Проекторы", menu_level="⚙️ Фрагмент в разработке").menu_buttons()
                    # await bot.send_message(callback.message.chat.id, 'Каталог проекторов: '
                    #                                              'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                    #                                              'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing')
                elif split_list[1] == "💰 Каталог(Сканеры)":
                    await Buttons(bot, callback.message, {}, "Barcode сканеры", menu_level="⚙️ Фрагмент в разработке").menu_buttons()
                    # await bot.send_message(callback.message.chat.id, 'Каталог сканеров: '
                    #                                              'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                    #                                              'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing')
                elif split_list[1] == "💰 Каталог(СФ)":
                    await bot.send_message(callback.message.chat.id, 'Каталог сетевых фильтров: '
                                                                 'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                                                                 'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing')
                elif split_list[1] == "💰 Каталог(аудио)":
                    await Buttons(bot, callback.message, {}, "Аудио аксессуары", menu_level="⚙️ Фрагмент в разработке").menu_buttons()
                    # await bot.send_message(callback.message.chat.id, 'Каталог аудио аксессуаров: '
                    #                                              'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                    #                                              'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing')
                elif split_list[1] == "💰 Каталог(хабы)":
                    await bot.send_message(callback.message.chat.id, 'Каталог OTG/Хабы/кардридеры: ',
                                           'https://docs.google.com/spreadsheets/d/1ZmC3cxYSyupkvNyevNKkpt4LiFniypUH/'
                                           'edit?usp=sharing&ouid=117298760559545275811&rtpof=true&sd=true')

                elif split_list[1] == "💰 Каталог(повербанки)":
                    await bot.send_message(callback.message.chat.id, 'Каталог Powerbanks/станции питания(BAVIN): ',
                                           'https://docs.google.com/spreadsheets/d/1ZmC3cxYSyupkvNyevNKkpt4LiFniypUH/'
                                           'edit?usp=sharing&ouid=117298760559545275811&rtpof=true&sd=true')
            else:
                await Buttons(bot, callback.message,
                              structure_menu["Основное меню"]["📦 Закупка оптом"][f'{split_list[0]}'][f'{split_list[1]}'],
                              back_button=f'{split_list[0]}',
                              menu_level="Пожалуйста выберите модель/серию:").menu_buttons()
                await state.update_data(brand=split_list[1])
                await state.set_state(Next_level_base.model)

        elif callback.data == 'Общая база клиентов':
            await bot.edit_message_text(text='База для рассылки: Общая база клиентов\nОтправь мне пост 💬',
                                        chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            await state.update_data(base=callback.data)
            await state.set_state(Rassylka.post)

        elif callback.data.startswith("💰 "):
            if callback.data == '💰 Каталог(CB)':
                await Buttons(bot, callback.message, {}, "Кабели", menu_level="⚙️ Фрагмент в разработке").menu_buttons()
                # await bot.send_message(callback.message.chat.id, 'Каталог кабелей: '
                #                                              'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                #                                              'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing')
            elif callback.data == "💰 Каталог(PC)":
                await Buttons(bot, callback.message, {}, "Блоки зарядки", menu_level="⚙️ Фрагмент в разработке").menu_buttons()
                # await bot.send_message(callback.message.chat.id, 'Каталог блоков зарядки: '
                #                                              'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                #                                              'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing')
            elif callback.data == "💰 Каталог(BH,MP)":
                await bot.send_message(callback.message.chat.id, 'Каталог беспроводных наушников: '
                                                             'https://docs.google.com/spreadsheets/d/1lc1tBWMCSOGKwdM-'
                                                                 'U6C7U1R3lRJLsUX99FCVAsaax5E/edit?usp=sharing')
            elif callback.data == "💰 Каталог(авто)":
                await Buttons(bot, callback.message, {}, "Зарядки в авто", menu_level="⚙️ Фрагмент в разработке").menu_buttons()
                # await bot.send_message(callback.message.chat.id, 'Каталог зарядок в авто: '
                #                                              'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                #                                              'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing')
            elif callback.data == "💰 Каталог(подставки)":
                await bot.send_message(callback.message.chat.id, 'Каталог держателей/подставок устройств: '
                                                             'https://docs.google.com/spreadsheets/d/1p4xQXqozQugy3N'
                                                                 'aHut3TUY6COqvzCgYb2AEMV1Cx6Zc/edit?usp=sharing')
            elif callback.data == "💰 Каталог(повербанки)":
                await Buttons(bot, callback.message, {}, "Powerbanks/станции питания", menu_level="⚙️ Фрагмент в разработке").menu_buttons()
                # await bot.send_message(callback.message.chat.id, 'Каталог повербанков/станций питания: '
                #                                              'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                #                                              'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing')
            elif callback.data == "💰 Каталог(зарядки)":
                await Buttons(bot, callback.message, {}, "Беспроводные зарядки", menu_level="⚙️ Фрагмент в разработке").menu_buttons()
                # await bot.send_message(callback.message.chat.id, 'каталог беспроводных зарядок: '
                #                                              'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                #                                              'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing')
        else:
            await state.update_data(model=callback.data)
            await bot.edit_message_text(text='Пожалуйста введите предполагаемое количество товара числом (в случае отмены отправьте 0)',
                                        chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            await state.set_state(Next_level_base.quantity)

    except Exception as e:
        logger.exception('Ошибка в handlers/check_callbacks', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/check_callbacks: {e}')



async def handler_user_message(message: Message):
    answer = await assistant_manager.get_response(message.text)
    await message.answer(answer, parse_mode='markdown')


