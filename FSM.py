# Импортируем необходимые классы из aiogram
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from configs.passwords import group_id
from google_sheets import Sheet_base


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
    nickname = State()


async def anoter_model_registration(message, state: FSMContext, bot):
    data = await state.get_data()
    data_marka = data.get('marka')
    await bot.send_message(message.chat.id, 'Cпасибо! Я передал информацию мастеру. Прайс будет выслан Вам '
                                                     'в ближайшее время.')
    await bot.send_message(group_id, f'🚨!!!СРОЧНО!!!🚨\n'
                           f'Хозяин, поступил запрос прайса на отсутствующее в моем списке авто от:\n\n'
                           f'Имя: {message.from_user.first_name}\n'
                           f'Фамилия: {message.from_user.last_name}\n'
                           f'Никнейм: {message.from_user.username}\n'
                           f'id чата: {message.chat.id}\n'
                           f'Ссылка: @{message.from_user.username}\n'
                           f'Авто: {data_marka} {message.text}\n\n'
                           f'Быстрее отправь прайс на его корыто пока он не слился.\n'
                           f'В случае положительной отработки заявки не забудь перевести клиента из базы '
                           f'"потенциальные клиенты" в базу "старые клиенты" с помощью команды:\n '
                           f'/next_level_base')
    # await clients_base(bot, message, auto_model=f'{data_marka} {message.text}').chec_and_record()
    await state.clear()


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
    data = await state.get_data()
    data_base = data.get('base')
    await Sheet_base(bot, message).rasylka_v_bazu()
    await state.clear()
#
#
# async def next_level(message, bot, state: FSMContext):
#     await clients_base(bot, message).perevod_v_bazu(message.text)
#     await state.clear()
