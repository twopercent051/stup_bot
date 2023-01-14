import random

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hcode

from tgbot.keyboards.inline import *
from tgbot.misc.states import FSMUser
from tgbot.models.db_connector import *
from tgbot.handlers.admin import admin_group
from create_bot import bot


async def user_start_msg(message: Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    is_user = await is_user_sql(user_id)
    if not is_user:
        await create_user_sql(user_id, username)
    text = [
        'Здравствуйте! Это бот стендап-клуба Stand-Up Station Antalya. Здесь можно забронировать стол на любое наше',
        'мероприятие, отредактировать вашу запись и связаться с менеджером. \n\n Пожалуйста, нажмите интересующее',
        'действие.'
    ]
    keyboard = user_mainmenu_kb()
    await FSMUser.home.set()
    await message.answer(' '.join(text), reply_markup=keyboard)


async def user_start_clb(callback: CallbackQuery):
    text = [
        'Здравствуйте! Это бот стендап-клуба Stand-Up Station Antalya. Здесь можно забронировать стол на любое наше',
        'мероприятие, отредактировать вашу запись и связаться с менеджером. \n\n Пожалуйста, нажмите интересующее',
        'действие.'
    ]
    keyboard = user_mainmenu_kb()
    await FSMUser.home.set()
    await callback.message.answer(' '.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)
    

async def record_table(callback: CallbackQuery):
    text = 'Выберите мероприятие, которое хотите посетить'
    events = await get_user_events_sql()
    keyboard = events_kb(events, False)
    await FSMUser.create_reg.set()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def click_event(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username_pr = callback.from_user.username
    if username_pr is None:
        user_username = ''
    else:
        user_username = f'@{username_pr}'
    event_id = callback.data.split(':')[1]
    is_registarted = await is_registrated_sql(str(user_id), event_id)
    event_capacity_pr = await get_event_capacity_sql(event_id)
    event_capacity = event_capacity_pr['capacity']
    event_total_pr = await get_total_regs_sql(event_id)
    if event_total_pr['SUM(number_persons)'] is None:
        event_total = 0
    else:
        event_total = event_total_pr['SUM(number_persons)']
    if is_registarted:
        text = f'Вы уже записаны на это мероприятие. Чтобы его отредактировать, нажмите клавишу'
        keyboard = edit_registration_kb()
        await callback.message.answer(text, reply_markup=keyboard)
        await bot.answer_callback_query(callback.id)
    elif event_total >= event_capacity:
        text_user = f'К сожалению, сейчас все места заняты, но мы вам сообщим сразу же, если они пояаятся'
        keyboard_user = home_kb()
        text_admin = f'⚠️ Посетителю {user_username} не удалось забронировать стол: всё занято'
        keyboard_admin = answer_kb(user_id)
        await callback.message.answer(text_user, reply_markup=keyboard_user)
        await bot.send_message(chat_id=admin_group, text=text_admin, reply_markup=keyboard_admin)
        await bot.answer_callback_query(callback.id)
    else:
        event_dict = await get_event_id_sql(event_id)
        event_dtime = get_rus_dtime(event_dict["dtime"], 'all')
        event_text = [
            f'<b>{event_dict["title"]}</b>',
            '',
            event_dict['description'],
            '',
            f'⏰ Встречаемся {event_dtime}',
            '',
            f'📌 Место встречи: {event_dict["location"]}'
        ]
        keyboard = home_kb()
        async with state.proxy() as data:
            data['event_id'] = event_id
            data['event_title'] = event_dict["title"]
            data['event_dtime'] = event_dict["dtime"]
            data['user_id'] = str(user_id)
            data['nick_name'] = user_username
        await FSMUser.number_persons.set()
        await bot.send_photo(chat_id=user_id, photo=event_dict['photo_id'], caption='\n'.join(event_text))
        time.sleep(2)
        await callback.message.answer('<b>На сколько человек вам нужен стол?</b>', reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def number_persons(message: Message, state: FSMContext):
    if message.text.isdigit():
        async with state.proxy() as data:
            data['persons'] = message.text
        text = 'Здорово! Где бы вы хотели сидеть?'
        keyboard = wish_kb()
        await FSMUser.wish.set()
    else:
        text = 'Вы ввели не число. Попробуйте снова'
        keyboard = home_kb()
    await message.answer(text, reply_markup=keyboard)


async def wish(callback: CallbackQuery, state: FSMContext):
    wish = callback.data.split(':')[1]
    async with state.proxy() as data:
        data['wish'] = wish
    async with state.proxy() as data:
        event_title = data.as_dict()['event_title']
        event_dtime = data.as_dict()['event_dtime']
        persons = data.as_dict()['persons']
    wish_text = None
    event_date = get_rus_dtime(event_dtime, 'date')
    if wish == 'closer':
        wish_text = 'И вы хотите сидеть поближе к сцене'
    if wish == 'further':
        wish_text = 'И вы хотите сидеть подальше от сцены'
    if wish == 'no_diff':
        wish_text = 'И вам без разницы где сидеть, главное хорошо провести время'
    text = [
        'Супер! Давайте проверим:\n',
        f'Вы бронируете стол на {event_title} {event_date} на {persons} человек',
        wish_text
    ]
    keyboard = accept_registaration_kb()
    await callback.message.answer(' '.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def registration_finish(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        event_id = data.as_dict()['event_id']
    table_list = await get_tables_not_event(event_id)
    table = random.choice(table_list)['table_name']
    async with state.proxy() as data:
        data['table'] = table
    text = [
        f'Вам забронирован стол по имени {hcode(table)}. Покажите это сообщение на входе\n',
        'Пожалуйста, измените запись в боте, если у вас что-то поменяется'
    ]
    keyboard = home_kb()
    await create_registration_sql(state)
    await callback.message.answer('\n'.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def edit_registrations(callback: CallbackQuery):
    user_id = callback.from_user.id
    registrations = await get_user_registrations(str(user_id))
    if len(registrations) == 0:
        text = 'Вы пока ничего не забронировали'
        keyboard = home_kb()
    else:
        text = 'Выберите запись для изменения'
        keyboard = events_kb(registrations, False)
    await FSMUser.edit_reg.set()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def edit_registration(callback: CallbackQuery, state: FSMContext):
    event_id = callback.data.split(':')[1]
    async with state.proxy() as data:
        data['event_id'] = event_id
    text = 'Выберите действие'
    keyboard = edit_reg_menu_kb()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def edit_persons(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    async with state.proxy() as data:
        event_id = data.as_dict()['event_id']
    persons_prev = await get_reg_persons(event_id, str(user_id))
    persons = persons_prev['number_persons']
    text = f'Сейчас записано {persons} человек. Отправьте новое количество.'
    keyboard = home_kb()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def new_persons(message: Message, state: FSMContext):
    if message.text.isdigit():
        user_id = message.from_user.id
        async with state.proxy() as data:
            event_id = data.as_dict()['event_id']
        await edit_persons_sql(event_id, str(user_id), message.text)
        text = 'Здорово! Мы внесли изменения'
        await FSMUser.wish.set()
    else:
        text = 'Вы ввели не число. Попробуйте снова'
    keyboard = home_kb()
    await message.answer(text, reply_markup=keyboard)



async def delete_reg(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    async with state.proxy() as data:
        event_id = data.as_dict()['event_id']
    await delete_registration_sql(event_id, str(user_id))
    text = 'Вы удалили запись.'
    keyboard = home_kb()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def write_to_admin(callback: CallbackQuery):
    text = 'Задайте свой вопрос, и мы ответим вам в ближайшее время'
    keyboard = home_kb()
    await FSMUser.support.set()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def answer_to_admin(callback: CallbackQuery):
    text = 'Нажмите ОТВЕТИТЬ для ответа'
    keyboard = home_kb()
    await FSMUser.support.set()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)

async def send_to_admin(message: Message):
    user_id = message.from_user.id
    username_pr = message.from_user.username
    if username_pr is None:
        user_username = ''
    else:
        user_username = f'@{username_pr}'
    text_user = 'Мы получили ваше сообщение, скоро ответим'
    keyboard_user = home_kb()
    text_admin = [
        f'⚠️ Новое сообщение от пользователя {user_username} :',
        '',
        message.text
    ]
    keyboard_admin = answer_kb(user_id)
    await FSMUser.home.set()
    await message.answer(text_user, reply_markup=keyboard_user)
    await bot.send_message(admin_group, text='\n'.join(text_admin), reply_markup=keyboard_admin)



def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start_msg, commands=["start"], state="*")
    dp.register_message_handler(number_persons, content_types='text', state=FSMUser.number_persons)
    dp.register_message_handler(new_persons, content_types='text', state=FSMUser.edit_reg)
    dp.register_message_handler(send_to_admin, content_types='text', state=FSMUser.support)

    dp.register_callback_query_handler(user_start_clb, lambda x: x.data == 'home', state='*')
    dp.register_callback_query_handler(record_table, lambda x: x.data in ['record', 'refuse_reg'], state='*')
    dp.register_callback_query_handler(click_event, lambda x: x.data.split(':')[0] == 'event', state=FSMUser.create_reg)
    dp.register_callback_query_handler(wish, lambda x: x.data.split(':')[0] == 'wish', state='*')
    dp.register_callback_query_handler(registration_finish, lambda x: x.data == 'accept_reg', state='*')
    dp.register_callback_query_handler(edit_registrations, lambda x: x.data == 'edit_reg', state='*')
    dp.register_callback_query_handler(edit_registration, lambda x: x.data.split(':')[0] == 'event',
                                       state=FSMUser.edit_reg)
    dp.register_callback_query_handler(edit_persons, lambda x: x.data == 'edit_persons', state=FSMUser.edit_reg)
    dp.register_callback_query_handler(delete_reg, lambda x: x.data == 'del_reg', state='*')
    dp.register_callback_query_handler(write_to_admin, lambda x: x.data == 'support', state='*')
    dp.register_callback_query_handler(answer_to_admin, lambda x: x.data.split(':')[0] == 'answer', state='*')

