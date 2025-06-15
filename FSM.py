# Импортируем необходимые классы из aiogram
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from configs.passwords import group_id, loggs_acc
from functions import get_usd_cny_rate
from google_sheets import find_product, get_sheet_base
from keyboards import Buttons
from structure import structure_menu


# Определяем класс для состояния message
class Get_admin(StatesGroup):
    message = State()


class Message_from_admin(StatesGroup):
    user_id = State()
    message = State()


class Rassylka(StatesGroup):
    base = State()
    post = State()


class Next_level_base(StatesGroup):
    kategoriya = State()
    brand = State()
    model = State()
    info = State()
    quantity = State()
    price = State()


class Get_product_info(StatesGroup):
    info = State()
    quantity = State()
    price = State()


async def message_from_user(message, state: FSMContext, bot):
    await bot.send_message(group_id, f'Сообщение от пользователя @{message.from_user.username}:')
    await bot.copy_message(group_id, message.chat.id, message.message_id)
    await bot.send_message(message.chat.id, 'Ваше сообщение отправлено ✅')
    await state.clear()


async def message_from_admin_chat(message, state: FSMContext, bot):
    if str.isdigit(message.text) is True:
        await state.update_data(user_id=message.text)
        await bot.send_message(message.chat.id, 'Введите сообщение')
        await state.set_state(Message_from_admin.message)
    else:
        await bot.send_message(message.chat.id, 'Неверные данные... Повтори попытку используя цифры (Например: 1338281106)')
        await state.set_state(Message_from_admin.user_id)


async def message_from_admin_text(message, state: FSMContext, bot):
    data = await state.get_data()
    user_id = data.get('user_id')
    await bot.copy_message(user_id, message.chat.id, message.message_id)
    await bot.send_message(message.chat.id, 'Ваше сообщение отправлено ✅')
    await state.clear()


async def rassylka(message, bot, state: FSMContext):
    # data = await state.get_data()
    # data_base = data.get('base')
    sheet_base = await get_sheet_base()
    await sheet_base.rasylka_v_bazu(bot, message)
    await state.clear()


async def save_all_user_information(message, state: FSMContext, bot):
    try:
        if str.isdigit(message.text) is True:
            if message.text == '0':
                await Buttons(bot, message, structure_menu["Основное меню"],
                              menu_level="Вы прервали оформление заявки.\nПожалуйста выберите "
                                         "интересующий пункт меню:").new_main_menu_buttons()
                await state.clear()
            else:
                data = await state.get_data()
                kategoriya = data.get('kategoriya')
                brand = data.get('brand')
                model = data.get('model')
                quantity = message.text
                await bot.send_message(chat_id=message.chat.id, text='<b>Заявка оформлена и передана администратору,</b> с Вами свяжутся в ближайшее время. '
                                                 'Спасибо, что выбрали нас.🤝\n\n'
                                                 'Для возвращения в главное меню воспользуйтесь командой /menu', parse_mode="html")
                sheet_base = await get_sheet_base()
                await sheet_base.record_in_base(bot, message, kategoriya, brand, model, quantity)
                await state.clear()
                await bot.send_message(group_id, f'🚨!!!СРОЧНО!!!🚨\n'
                                                 f'<b>Поступила ЗАЯВКА от:</b>\n'
                                                 f'Псевдоним: @{message.from_user.username}\n'
                                                 f'id чата: {message.chat.id}\n\n'
                                                 f'<b>Предмет интереса:</b>\n'
                                                 f'категория: {kategoriya}\n'
                                                 f'бренд: {brand}\n'
                                                 f'модель: {model}\n'
                                                 f'количество: {quantity}\n'
                                                 f'Быстрее согласуйте дату и закройте заявку пока он не слился\n'
                                                 f'/sent_message - отправить сообщение с помощью бота\n\n'
                                                 f'<b>Дополнительная информация в гугл таблице: </b>https://docs.google.com/spread'
                                                 f'sheets/d/1upFEYAoBg1yio5oC2KFX6WMb0FDBslw-NplIXHNzR9Y/edit?usp=sharing',
                                       parse_mode='html')
                await state.clear()
        else:
            await bot.send_message(message.chat.id, 'Неверные данные... Повторите попытку, используя цифры (Например: 11)')
            await state.set_state(Next_level_base.quantity)
    except Exception as e:
        logger.exception('Ошибка в FSM/save_all_user_information', e)
        await bot.send_message(loggs_acc, f'Ошибка в FSM/save_all_user_information: {e}')

#
# async def next_level(message, bot, state: FSMContext):
#     await clients_base(bot, message).perevod_v_bazu(message.text)
#     await state.clear()

async def count_price_step_one(callback, bot, state: FSMContext):
    try:
        product_list = await find_product(callback.data)
        if '__' in callback.data:
            split_list = callback.data.split('__')
            data = await state.get_data()
            if split_list[0] == data.get("kategoriya"):
                await Buttons(bot, callback.message,
                              structure_menu["Основное меню"]["📦 Закупка оптом"][f'{split_list[0]}'][f'{split_list[1]}'],
                              back_button=f'{split_list[0]}',
                              menu_level="Пожалуйста выберите модель/серию:").menu_buttons()

                await state.set_state(Next_level_base.model)
            else:
                await state.update_data(info=product_list)
                await bot.edit_message_text(
                    text='Пожалуйста введите количество товара числом (в случае отмены отправьте 0)',
                    chat_id=callback.message.chat.id, message_id=callback.message.message_id)
                await state.set_state(Next_level_base.quantity)
        elif callback.data == "Основное меню":
            await state.clear()
            await Buttons(bot, callback.message, structure_menu["Основное меню"], menu_level= "Пожалуйста выберите интересующий пункт меню:").menu_buttons()
        else:
            await state.set_state(Next_level_base.model)
            await Buttons(bot, callback.message, keys_dict=None).speed_find_of_product_buttons(product_list)
    except Exception as e:
        logger.exception('Ошибка в FSM/count_price_step_one', e)
        await bot.send_message(loggs_acc, f'Ошибка в FSM/count_price_step_one: {e}')


async def count_price_step_two(message, state: FSMContext, bot):
    try:
        if str.isdigit(message.text) is True:
            data = await state.get_data()
            if message.text == '0':
                await Buttons(bot, message, structure_menu["Основное меню"],
                              menu_level="Вы прервали оформление заявки.\nПожалуйста выберите "
                                         "интересующий пункт меню:").new_main_menu_buttons()
                await state.clear()

            elif int(message.text) < int(data.get('info')[0]['MOQ, шт']):
                await bot.send_message(message.chat.id, f"Минимальное количество заказа (MOQ) данной модели: "
                                                        f"{data.get('info')[0]['MOQ, шт']} шт.")
                await state.set_state(Next_level_base.quantity)

            else:
                mess = await bot.send_message(text='Считаем..🚀', chat_id=message.chat.id)
                usd_uan = await get_usd_cny_rate()
                uan_rate = float(usd_uan['CNY'])
                usd_rate = float(usd_uan['USD'])
                price_uan = float(data.get('info')[0]['Столбец 1'].replace(",", ".")) if data.get('info')[0]['Столбец 1'] else 0
                quantity = int(message.text)
                logistic_price_of_MOQ = float(data.get('info')[0]['Стоимость логистики за MOQ, $'].replace(",", ".")) if data.get('info')[0]['Стоимость логистики за MOQ, $'] else 0
                end_price = ((price_uan * uan_rate * quantity) + (usd_rate * logistic_price_of_MOQ)*1.2)
                await state.update_data(quantity=quantity)
                await state.update_data(price=end_price)
                await Buttons(bot, mess, None, menu_level=f'<b>Расчет итоговой цены:</b>\n\n'
                              f'<b>Модель:</b> {data.get("info")[0]["Модель"]}\n'
                              f'<b>Артикул:</b> {data.get("info")[0]["Артикул товара"]}\n'
                              f'<b>Количество, шт:</b> {quantity}\n'
                              f'<b>Итоговая цена, ₽:</b> {end_price}\n').zayavka_buttons()

                await state.set_state(Next_level_base.price)
        else:
            await bot.send_message(message.chat.id, 'Неверные данные... Повторите попытку, используя цифры (Например: 11)')
            await state.set_state(Next_level_base.quantity)
    except Exception as e:
        logger.exception('Ошибка в FSM/count_price_step_two', e)
        await bot.send_message(loggs_acc, f'Ошибка в FSM/count_price_step_two: {e}')


async def handler_user_message_info(message, bot, state: FSMContext):
    try:
        product_list = await find_product(message.text)
        if product_list is not None:
            await Buttons(bot, message, keys_dict=None).speed_find_of_product_buttons(product_list)
            if len(product_list) == 1:
                await state.set_state(Next_level_base.info)
        else:
            try:
                await bot.edit_message_text(
                    text="<b>Пожалуйста введите название</b> (для обозначения букв допускается только "
                    "латиница) <b>или артикул модели</b>\n\n(Пример: CA-67 (название), 6936985015064"
                    " (артикул)).\n\n Название, артикул и полный перечень информации по товарам "
                    'смотрите в каталогах доступных по кнопке <b>"📋 Каталоги товаров и цен"</b> в '
                    "основном меню",
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    parse_mode="html",
                )
                await state.set_state(Next_level_base.info)
            except TelegramBadRequest:
                await bot.send_message(chat_id=message.chat.id, text='<b>Пожалуйста введите название</b> '
                                                                          '(для обозначения букв допускается только '
                                                                          'латиница) <b>или артикул модели</b>\n\n'
                                                                          '(Пример: CA-67 (название), 6936985015064'
                                                                          ' (артикул)).\n\n Название, артикул и полный '
                                                                          'перечень информации по товарам смотрите в '
                                                                          'каталогах доступных по кнопке '
                                                                          '<b>"📋 Каталоги товаров и цен"</b> в "основном '
                                                                          'меню"', parse_mode="html")
                await state.set_state(Next_level_base.info)
    except Exception as e:
        logger.exception('Ошибка в FSM/handler_user_message_info', e)
        await bot.send_message(loggs_acc, f'Ошибка в FSM/handler_user_message_info: {e}')
