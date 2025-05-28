import asyncio

import pytz
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from assistent import get_assistant_manager
from configs.passwords import admins_list, group_id, loggs_acc
from FSM import Get_admin, Message_from_admin, Next_level_base, Rassylka
from google_sheets import find_product, get_sheet_base, data_updater
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
                                                     '/reload_tables - перезагрузка таблиц\n'
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


async def reload_tables(message: Message, bot, state: FSMContext):
    try:
        await state.clear()
        if message.chat.id in admins_list:
            mess = await message.answer('Загрузка..🚀')
            data_updater()
            await bot.edit_message_text(chat_id=message.chat.id, text="Таблицы успешно обновлены.", message_id=mess.message_id)
        else:
            await bot.send_message(message.chat.id, 'У Вас нет прав для использования данной команды')
    except Exception as e:
        logger.exception('Ошибка в handlers/reload_tables', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/reload_tables: {e}')


async def day_visitors(message: Message, bot, state: FSMContext):
    await state.clear()
    today_list = []
    mess = await bot.send_message(message.chat.id, 'Загрузка..🚀')
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
    assert callback is not None   # обозначаем для проверочной библиотеки mypy, чтобы избегать лишних ошибок при тесте
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
            await bot.send_message(chat_id=callback.message.chat.id, text='<b>Каталог сетевых фильтров: </b>'
                                                             'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                                                             'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing',
                                   parse_mode='html')
            await asyncio.sleep(0.2)
            await bot.send_message(chat_id=callback.message.chat.id, text='<b>Каталог OTG/Хабы/кардридеры: </b>'
                                   'https://docs.google.com/spreadsheets/d/1s2dyd9fHWVtBJLGWO4JT2AUskRXvUaFwFFrh1ikp8i0'
                                   '/edit?usp=sharing', parse_mode='html')
            await asyncio.sleep(0.2)
            await bot.send_message(chat_id=callback.message.chat.id, text='<b>Каталог беспроводных наушников: </b>'
                                                             'https://docs.google.com/spreadsheets/d/1lc1tBWMCSOGKwdM-'
                                                             'U6C7U1R3lRJLsUX99FCVAsaax5E/edit?usp=sharing',
                                   parse_mode='html')
            await asyncio.sleep(0.2)
            await bot.send_message(chat_id=callback.message.chat.id, text='<b>Каталог держателей/подставок устройств: </b>'
                                                             'https://docs.google.com/spreadsheets/d/1p4xQXqozQugy3N'
                                                             'aHut3TUY6COqvzCgYb2AEMV1Cx6Zc/edit?usp=sharing',
                                   parse_mode='html')
            await asyncio.sleep(0.2)
            await bot.send_message(chat_id=callback.message.chat.id, text='<b>Каталог Powerbanks/станции питания(BAVIN):</b> '
                                   'https://docs.google.com/spreadsheets/d/1xfIx2SMaWnR88xPWY2tZ0fzLVTes2D8HMWxZBtbXGFs'
                                   '/edit?usp=sharing', parse_mode='html')
            await asyncio.sleep(0.2)
            await bot.send_message(chat_id=callback.message.chat.id, text='<b>Каталог зарядок в авто(BAVIN):</b> '
                                        'https://docs.google.com/spreadsheets/d/1_IxmDysMNlruynERjTqcfKrLdSPS9Va3WlzLL'
                                        'B92g_M/edit?usp=sharing', parse_mode='html')
            await asyncio.sleep(0.2)
            await bot.send_message(chat_id=callback.message.chat.id, text='<b>Беспроводные зарядки(BAVIN):</b> '
                                   'https://docs.google.com/spreadsheets/d/1HISN8oq8UawoT721ckVDYYTIJCoA0p0VtZ8wYXB25P'
                                   'o/edit?usp=sharing', parse_mode='html')
            await asyncio.sleep(0.2)
            await bot.send_message(chat_id=callback.message.chat.id, text='<b>Аудио аксессуары(BAVIN):</b> '
                                   'https://docs.google.com/spreadsheets/d/1IbLXLZteFidJ0jqW5Hq1b9Z0GTgyB-cYPou_4oV1_'
                                   '-4/edit?gid=1246518664#gid=1246518664', parse_mode='html')
            await asyncio.sleep(0.2)
            await bot.send_message(chat_id=callback.message.chat.id, text='<b>Каталог блоков зарядки(BAVIN):</b> '
                                   'https://docs.google.com/spreadsheets/d/1d4EHBeFg-SVMvkc12dnQTNd_vYjsi-Vb/edit?usp='
                                   'sharing&ouid=117298760559545275811&rtpof=true&sd=true', parse_mode='html')
            await asyncio.sleep(0.2)
            await bot.send_message(chat_id=callback.message.chat.id, text='<b>Каталог серверных комплектующих:</b> '
                                   'https://docs.google.com/spreadsheets/d/1XJlkP2ro0EXX3ZudN__Z5Y4e5G2HLhsu/edit?usp='
                                   'sharing&ouid=117298760559545275811&rtpof=true&sd=true', parse_mode='html')

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

            await bot.send_message(chay_id=group_id, text=f'🚨!!!СРОЧНО!!!🚨\n'
                                            f'<b>поступил запрос на ЧАТ С АДМИНИСТРАТОРОМ от:</b>\n'
                                            f'Ссылка: @{callback.from_user.username}\n'
                                            f'id чата: {callback.message.chat.id}\n'
                                            f'<b>Если ссылка на чат отсутствует запроси контакт или отправь свой с помощью команды</b>:\n'
                                            f'/sent_message - отправить сообщение с помощью бота', parse_mode="html")
            await state.set_state(Get_admin.message)

        elif callback.data == "ℹ️ О нас":
            await Buttons(bot, callback.message, {},"Основное меню", menu_level="⚙️ Фрагмент в разработке").menu_buttons()

        elif callback.data == "Основное меню":
            await state.clear()
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

        elif callback.data in '✅ Оформить заявку':
            if '✅' in callback.data:
                data = await state.get_data()
                kategoriya = data.get('kategoriya')
                brand = data.get('brand')
                info = data.get('info')
                quantity = data.get('quantity')
                price = data.get('price')
                model = info[0]["Модель"]
                await bot.send_message(chat_id=callback.message.chat.id,
                                       text='<b>Заявка оформлена и передана администратору,</b> с Вами свяжутся в ближайшее время. '
                                            'Спасибо, что выбрали нас.🤝\n\n'
                                            'Для возвращения в главное меню воспользуйтесь командой /menu',
                                       parse_mode="html")
                await callback.message.edit_reply_markup(reply_markup=None)
                sheet_base = await get_sheet_base()
                await sheet_base.record_in_base(bot, callback.message, kategoriya=kategoriya, brand=brand, model=model,
                                                quantity=quantity, end_price=price)
                await state.clear()
                await bot.send_message(group_id, f'🚨!!!СРОЧНО!!!🚨\n'
                                                 f'<b>Поступила ЗАЯВКА от:</b>\n'
                                                 f'Псевдоним: @{callback.from_user.username}\n'
                                                 f'id чата: {callback.message.chat.id}\n\n'
                                                 f'<b>Предмет интереса:</b>\n'
                                                 f'категория: {kategoriya}\n'
                                                 f'бренд: {brand}\n'
                                                 f'модель: {model}\n'
                                                 f'количество: {quantity}\n'
                                                 f'Итоговая цена: {price}\n'
                                                 f'Быстрее согласуйте дату и закройте заявку пока он не слился\n'
                                                 f'/sent_message - отправить сообщение с помощью бота\n\n'
                                                 f'<b>Дополнительная информация в гугл таблице: </b>https://docs.google.com/spread'
                                                 f'sheets/d/1upFEYAoBg1yio5oC2KFX6WMb0FDBslw-NplIXHNzR9Y/edit?usp=sharing',
                                       parse_mode='html')
                await state.clear()

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
                    await bot.send_message(chat_id=callback.message.chat.id, text='Каталог сетевых фильтров: '
                                                                 'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                                                                 'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing')

                elif split_list[1] == "💰 Каталог(хабы)":
                    await bot.send_message(chat_id=callback.message.chat.id, text='Каталог OTG/Хабы/кардридеры: '
                                           'https://docs.google.com/spreadsheets/d/1s2dyd9fHWVtBJLGWO4JT2AUskRXvUaFwF'
                                           'Frh1ikp8i0/edit?usp=sharing')

                elif split_list[1] == "💰 Каталог(аудио)":
                    await bot.send_message(chat_id=callback.message.chat.id, text='Аудио аксессуары(BAVIN): '
                                           'https://docs.google.com/spreadsheets/d/1IbLXLZteFidJ0jqW5Hq1b9Z0GTgyB-cYPou'
                                           '_4oV1_-4/edit?gid=1246518664#gid=1246518664')

            elif await find_product(callback.data) is not None:
                await Buttons(bot, callback.message, back_button=split_list[1],
                              keys_dict=None).speed_find_of_product_buttons(await find_product(callback.data))
                await state.set_state(Next_level_base.info)

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
                # await bot.send_message(chat_id=callback.message.chat.id, text='Каталог кабелей: '
                #                                              'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                #                                              'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing')
            elif callback.data == "💰 Каталог(PC)":
                # await Buttons(bot, callback.message, {}, "Блоки зарядки", menu_level="⚙️ Фрагмент в разработке").menu_buttons()
                await bot.send_message(chat_id=callback.message.chat.id, text='Каталог блоков зарядки: '
                                                             'https://docs.google.com/spreadsheets/d/1bd_lMkz7JqT_08MBA'
                                                             'IqBBwzgSyw2zMSiso-c0js6lFI/edit?usp=sharing')
            elif callback.data == "💰 Каталог(BH,MP)":
                await bot.send_message(chat_id=callback.message.chat.id, text='Каталог беспроводных наушников: '
                                                             'https://docs.google.com/spreadsheets/d/1lc1tBWMCSOGKwdM-'
                                                                 'U6C7U1R3lRJLsUX99FCVAsaax5E/edit?usp=sharing')
            elif callback.data == "💰 Каталог(авто)":
                await bot.send_message(chat_id=callback.message.chat.id, text='Каталог зарядок в авто: '
                                       'https://docs.google.com/spreadsheets/d/1_IxmDysMNlruynERjTqcfKrLdSPS9Va3WlzLL'
                                       'B92g_M/edit?usp=sharing')

            elif callback.data == "💰 Каталог(подставки)":
                await bot.send_message(chat_id=callback.message.chat.id, text='Каталог держателей/подставок устройств: '
                                                             'https://docs.google.com/spreadsheets/d/1p4xQXqozQugy3N'
                                                                 'aHut3TUY6COqvzCgYb2AEMV1Cx6Zc/edit?usp=sharing')
            elif callback.data == "💰 Каталог(повербанки)":
                # await Buttons(bot, callback.message, {}, "Powerbanks/станции питания", menu_level="⚙️ Фрагмент в разработке").menu_buttons()
                await bot.send_message(chat_id=callback.message.chat.id, text='Каталог повербанков/станций питания: '
                                       'https://docs.google.com/spreadsheets/d/1xfIx2SMaWnR88xPWY2tZ0fzLVTes2D8HMWxZBtb'
                                       'XGFs/edit?usp=sharing')

            elif callback.data == "💰 Каталог(зарядки)":
                # await Buttons(bot, callback.message, {}, "Беспроводные зарядки", menu_level="⚙️ Фрагмент в разработке").menu_buttons()
                await bot.send_message(chat_id=callback.message.chat.id, text='каталог беспроводных зарядок(BAVIN): '
                                       'https://docs.google.com/spreadsheets/d/1HISN8oq8UawoT721ckVDYYTIJCoA0p0VtZ8wY'
                                       'XB25Po/edit?usp=sharing')
        elif await find_product(callback.data) is not None:
            product_list = await find_product(callback.data)
            await Buttons(bot, callback.message, keys_dict=None).speed_find_of_product_buttons(product_list)
            if len(product_list) == 1:
                await state.set_state(Next_level_base.info)
        else:
            await state.update_data(model=callback.data)
            await bot.edit_message_text(text='<b>Пожалуйста введите название</b> (для обозначения букв допускается только '
                                             'латиница) <b>или артикул модели</b>\n\n(Пример: CA-67 (название), 6936985015064'
                                             ' (артикул)).\n\n Название, артикул и полный перечень информации по товарам '
                                             'смотрите в каталогах доступных по кнопке <b>"📋 Каталоги товаров и цен"</b> в '
                                             'основном меню', chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id, parse_mode='html')
            # await state.set_state(Next_level_base.quantity)

    except Exception as e:
        logger.exception('Ошибка в handlers/check_callbacks', e)
        await bot.send_message(loggs_acc, f'Ошибка в handlers/check_callbacks: {e}')



async def handler_user_message(message: Message, bot, state: FSMContext):
    await state.clear()
    product_list = await find_product(message.text)
    if product_list is not None:
        await Buttons(bot, message, keys_dict=None).speed_find_of_product_buttons(product_list)
        if len(product_list) == 1:
            await state.set_state(Next_level_base.info)
    else:
        assistant = await get_assistant_manager()
        answer = await assistant.get_response(message.text)
        await message.answer(answer)


