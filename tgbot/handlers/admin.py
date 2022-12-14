import os

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.inline import *
from tgbot.config import load_config
from tgbot.models.db_connector import *
from tgbot.misc.states import FSMEvent
from create_bot import bot

config = load_config(".env")
admin_group = config.misc.admin_group

async def admin_start_msg(message: Message):
    text = [
        'Это панель администратора. Тут можно и нужно создавать мероприятия, смотреть зарегистрированных пользователей',
        'и наверное много чего ещё. Это первое, что я написал, когда созавал бота, поэтому не знаю что получится.',
        'Нате вам смайлик ✌️'
    ]
    keyboard = admin_mainmenu_kb()
    await FSMEvent.home.set()
    await message.answer(' '.join(text), reply_markup=keyboard)


async def admin_start_clb(callback: CallbackQuery):
    text = [
        'Это панель администратора. Тут можно и нужно создавать мероприятия, смотреть зарегистрированных пользователей',
        'и наверное много чего ещё. Это первое, что я написал, когда созавал бота, поэтому не знаю что получится.',
        'Нате вам смайлик ✌️'
    ]
    keyboard = admin_mainmenu_kb()
    await FSMEvent.home.set()
    await callback.message.answer(' '.join(text), reply_markup=keyboard)


async def admin_event_menu(callback: CallbackQuery):
    text = 'Действуй!'
    keyboard = admin_event_menu_kb()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def create_event(callback: CallbackQuery):
    text = [
        'В этом меню вам нужно будет ввести все данные для наступающего мероприятия. Все поля, как вы их заполните',
        'попадут в каталог, который увидят посетители. Мероприятие будет опубликовано немедленно',
        '\n',
        '<b>А теперь введите название для мероприятия!</b>'
    ]
    keyboard = home_kb()
    await FSMEvent.title.set()
    await callback.message.answer(' '.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def create_event_title(message: Message, state: FSMContext):
    text = 'ЗДОРОВО! Теперь напишите дату мероприятия'
    keyboard = home_kb()
    title = message.text
    async with state.proxy() as data:
        data['title'] = title
    await FSMEvent.date.set()
    await message.answer(text, reply_markup=keyboard)


async def create_event_date(message: Message, state: FSMContext):
    text = 'Напишите во сколько будет мероприятие'
    keyboard = home_kb()
    date = message.text
    async with state.proxy() as data:
        data['date'] = date
    await FSMEvent.time.set()
    await message.answer(text, reply_markup=keyboard)


async def create_event_time(message: Message, state: FSMContext):
    text = 'Укажите место, где оно пройдёт'
    keyboard = home_kb()
    time = message.text
    async with state.proxy() as data:
        data['time'] = time
    await FSMEvent.location.set()
    await message.answer(text, reply_markup=keyboard)


async def create_event_location(message: Message, state: FSMContext):
    text = 'Загрузите афишу.'
    keyboard = home_kb()
    location = message.text
    async with state.proxy() as data:
        data['location'] = location
    await FSMEvent.picture.set()
    await message.answer(text, reply_markup=keyboard)


async def create_event_picture(message: Message, state: FSMContext):
    text = 'Сделайте описание.'
    keyboard = home_kb()
    photo_id = message.photo[-1].file_id
    async with state.proxy() as data:
        data['photo_id'] = photo_id
    await FSMEvent.description.set()
    await message.answer(text, reply_markup=keyboard)

async def edit_desc(callback: CallbackQuery):
    text = 'Сделайте описание.'
    keyboard = home_kb()
    await FSMEvent.description.set()
    await callback.message.answer(text, reply_markup=keyboard)

async def create_event_description(message: Message, state: FSMContext):
    async with state.proxy() as data:
        title = data.as_dict()['title']
        date = data.as_dict()['date']
        time = data.as_dict()['time']
        location = data.as_dict()['location']
        photo_id = data.as_dict()['photo_id']
    description = message.text
    text = [
        'Вот так это будет выглядеть:',
        f'<b>{title}</b>',
        '',
        description,
        '',
        f'⏰ Встречаемся {date} в {time}',
        f'📌 Место встречи: {location}',
        'Подтвердите или начните заново'
    ]
    async with state.proxy() as data:
        data['description'] = description
    await FSMEvent.description.set()
    try:
        keyboard = public_event_kb()
        await bot.send_photo(chat_id=admin_group, photo=photo_id, caption='\n'.join(text), reply_markup=keyboard)
    except:
        err_msg = "\n".join(text)
        text = f'Текст превышает максимально допустимую длину на {len(err_msg) - 964} символов'
        keyboard = too_long_desc_kb()
        await message.answer(text, reply_markup=keyboard)

async def public_event(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        title = data.as_dict()['title']
    text = f'Мероприятие <b>{title}</b> опубликовано!'
    keyboard = home_kb()
    await create_event_sql(state)
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)

async def incorrect_message(message: Message):
    text = 'Вы ввели некорректные данные. попробуйте снова или вернитесь в главное меню'
    keyboard = home_kb()
    await message.answer(text, reply_markup=keyboard)


async def show_tables(callback: CallbackQuery):
    text = ['<b>Сейчас список столов такой:</b>', '']
    tables = await get_tables()
    for table in tables:
        text.append(table['table_name'])
    keyboard = edit_tables_kb()
    await callback.message.answer('\n'.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)

async def new_tables(callback: CallbackQuery):
    text = [
        'Введите новые столы списком через ENTER',
        '⚠️ВНИМАНИЕ! Будет перезаписан весь список, при необходимости скопируйте предыдущее сообщение'
    ]
    keyboard = home_kb()
    await FSMEvent.tables.set()
    await callback.message.answer('\n'.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def edit_tables_finish(message: Message):
    text = 'Изменения сохранены'
    keyboard = home_kb()
    new_tables = message.text.split('\n')
    await delete_tables_sql()
    for table in new_tables:
        await create_table_sql(table)
    await message.answer(text, reply_markup=keyboard)



def register_admin(dp: Dispatcher):
    error_states = [FSMEvent.title, FSMEvent.date, FSMEvent.time, FSMEvent.location, FSMEvent.description]
    dp.register_message_handler(admin_start_msg, commands=["start"], state="*", chat_id=admin_group)
    dp.register_message_handler(create_event_title, state=FSMEvent.title, content_types='text', chat_id=admin_group)
    dp.register_message_handler(create_event_date, state=FSMEvent.date, content_types='text', chat_id=admin_group)
    dp.register_message_handler(create_event_time, state=FSMEvent.time, content_types='text', chat_id=admin_group)
    dp.register_message_handler(create_event_location, state=FSMEvent.location, content_types='text',
                                chat_id=admin_group)
    dp.register_message_handler(create_event_picture, state=FSMEvent.picture, content_types='photo',
                                chat_id=admin_group)
    dp.register_message_handler(incorrect_message, state=FSMEvent.picture, content_types=['text', 'video', 'sticker'],
                                chat_id=admin_group)
    dp.register_message_handler(create_event_description, state=FSMEvent.description, content_types='text',
                                chat_id=admin_group)
    dp.register_message_handler(incorrect_message, state=error_states, content_types=['photo', 'video', 'sticker'],
                                chat_id=admin_group)
    dp.register_message_handler(edit_tables_finish, state=FSMEvent.tables, content_types='text', chat_id=admin_group)


    dp.register_callback_query_handler(admin_start_clb, lambda x: x.data == 'home', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(admin_event_menu, lambda x: x.data == 'events', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(create_event, lambda x: x.data == 'create_event', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(public_event, lambda x: x.data == 'public', state=FSMEvent.description,
                                       chat_id=admin_group)
    dp.register_callback_query_handler(edit_desc, lambda x: x.data == 'edit_desc', state=FSMEvent.description,
                                       chat_id=admin_group)
    dp.register_callback_query_handler(show_tables, lambda x: x.data == 'tables', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(new_tables, lambda x: x.data == 'edit_tables', state='*', chat_id=admin_group)

