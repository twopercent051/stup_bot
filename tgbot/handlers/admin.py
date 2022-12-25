import random
import os

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hcode

from tgbot.keyboards.inline import *
from tgbot.models.db_connector import *
from tgbot.misc.states import FSMEvent
from tgbot.misc.datetime_handler import *
from tgbot.misc.list_creator import create_csv
from create_bot import bot, config

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
        '\n\n',
        '<b>А теперь введите название мероприятия!</b>'
    ]
    keyboard = home_kb()
    await FSMEvent.title.set()
    await callback.message.answer(' '.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def create_event_title(message: Message, state: FSMContext):
    text = 'ЗДОРОВО! Теперь напишите дату и время мероприятия в формате dd.mm.yyyy hh:mm'
    keyboard = home_kb()
    title = message.text
    async with state.proxy() as data:
        data['title'] = title
    await FSMEvent.dtime.set()
    await message.answer(text, reply_markup=keyboard)



async def create_event_dtime(message: Message, state: FSMContext):
    dt_event = message.text
    dt_stamp = get_datetime_stamp(dt_event)
    if dt_stamp is None:
        text = 'Неправильный формат или дата уже прошла'
        keyboard = home_kb()
    else:
        async with state.proxy() as data:
            data['dtime'] = dt_stamp
        text = 'Укажите место, где оно пройдёт'
        keyboard = home_kb()
        await FSMEvent.location.set()
    await message.answer(text, reply_markup=keyboard)


async def edit_event_dtime(callback: CallbackQuery):
    text = 'Напишите дату и время мероприятия в формате dd.mm.yyyy hh:mm'
    keyboard = home_kb()
    await FSMEvent.dtime.set()
    await callback.message.answer(text, reply_markup=keyboard)


async def create_event_location(message: Message, state: FSMContext):
    text = 'Укажите максимальную вместимость заведения'
    keyboard = home_kb()
    location = message.text
    async with state.proxy() as data:
        data['location'] = location
    await FSMEvent.capacity.set()
    await message.answer(text, reply_markup=keyboard)


async def create_event_capacity(message: Message, state: FSMContext):
    if message.text.isdigit():
        text = 'Загрузите афишу.'
        capacity = message.text
        async with state.proxy() as data:
            data['capacity'] = capacity
        await FSMEvent.picture.set()
    else:
        text = 'Вы ввели не число. Попробуйте еще раз'
    keyboard = home_kb()
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
        dtime = data.as_dict()['dtime']
        location = data.as_dict()['location']
        photo_id = data.as_dict()['photo_id']
    description = message.text
    event_dtime = get_rus_dtime(dtime, 'all')
    text = [
        'Вот так это будет выглядеть:',
        f'<b>{title}</b>',
        '',
        description,
        '',
        f'⏰ Встречаемся {event_dtime}',
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


async def answer_user_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.data.split(':')[1]
    text = 'Нажмите ОТВЕТИТЬ для ответа'
    keyboard = home_kb()
    async with state.proxy() as data:
        data['user_id'] = user_id
    await FSMEvent.answer.set()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def answer_user_finish(message: Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = data.as_dict()['user_id']
    text_admin = 'Сообщение отправлено'
    keyboard_admin = home_kb()
    text_user = [
        '⚠️ Сообщение от администратора:',
        '',
        message.text
    ]
    keyboard_user = answer_kb(admin_group)
    await FSMEvent.home.set()
    await message.answer(text_admin, reply_markup=keyboard_admin)
    await bot.send_message(user_id, text='\n'.join(text_user), reply_markup=keyboard_user)


async def show_events(callback: CallbackQuery):
    text = 'Показываются только будущие события и прошедшие не старше 7 дней'
    events = await get_admin_events_sql()
    keyboard = events_kb(events, True)
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def event_info(callback: CallbackQuery, state: FSMContext):
    event_id = callback.data.split(':')[1]
    async with state.proxy() as data:
        data['event_id'] = event_id
    event_dict = await get_event_id_sql(event_id)
    reg_dict = await get_total_regs_sql(event_id)
    event_dtime = get_rus_dtime(event_dict["dtime"], 'all')
    if reg_dict['SUM(number_persons)'] is None:
        event_total = 0
    else:
        event_total = reg_dict['SUM(number_persons)']
    text = [
        f'Информация по мероприятию <b>{event_dict["title"]}:</b>',
        f'Место: <i>{event_dict["location"]}</i>',
        f'Дата-время: <i>{event_dtime}</i>',
        f'Забронированно: <i>{reg_dict["COUNT(id)"]}</i> столов на <i>{event_total}</i> человек'
    ]
    keyboard = admin_event_kb()
    await callback.message.answer('\n'.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def manual_reg_start(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        event_id = data.as_dict()['event_id']
    event_capacity_pr = await get_event_capacity_sql(event_id)
    event_capacity = event_capacity_pr['capacity']
    event_total_pr = await get_total_regs_sql(event_id)
    if event_total_pr['SUM(number_persons)'] is None:
        event_total = 0
    else:
        event_total = event_total_pr['SUM(number_persons)']
    if event_total >= event_capacity:
        text = 'К сожалению, сейчас все места заняты'
    else:
        text = 'Введите количество зрителей'
        await FSMEvent.persons.set()
    keyboard = home_kb()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def manual_reg_persons(message: Message, state: FSMContext):
    if message.text.isdigit():
        async with state.proxy() as data:
            data['persons'] = message.text
        text = 'Контакт гостя'
        keyboard = home_kb()
        await FSMEvent.nickname.set()
    else:
        text = 'Вы ввели не число. Попробуйте снова'
        keyboard = home_kb()
    await message.answer(text, reply_markup=keyboard)


async def manual_reg_nickname(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['nick_name'] = message.text
    text = 'Какой предпочтение?'
    keyboard = wish_kb()
    await FSMEvent.wish.set()
    await message.answer(text, reply_markup=keyboard)

async def manual_reg_wish(callback: CallbackQuery, state: FSMContext):
    wish = callback.data.split(':')[1]
    async with state.proxy() as data:
        data['wish'] = wish
    async with state.proxy() as data:
        persons = data.as_dict()['persons']
    wish_text = None
    if wish == 'closer':
        wish_text = 'поближе к сцене'
    if wish == 'further':
        wish_text = 'подальше от сцены'
    if wish == 'no_diff':
        wish_text = 'без разницы где сидеть'
    text = [
        'Здорово! Давайте проверим:',
        f'Вы бронируете стол на {persons} человек, {wish_text}'
    ]
    keyboard = accept_registaration_kb()
    await callback.message.answer('\n'.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def registration_finish(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        event_id = data.as_dict()['event_id']
    table_list = await get_tables_not_event(event_id)
    table = random.choice(table_list)['table_name']
    async with state.proxy() as data:
        data['table'] = table
        data['user_id'] = 0
    text = f'Забронирован стол {hcode(table)}. Перешлите это сообщение клиенту'
    keyboard = home_kb()
    await create_registration_sql(state)
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def edit_registration_start(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        event_id = data.as_dict()['event_id']
    reg_list = await get_list_sql(event_id)
    if len(reg_list) == 0:
        text = 'Записей нет'
    else:
        text = 'Выберите запись для редактирования'
    keyboard = reg_list_kb(reg_list)
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def edit_registration(callback: CallbackQuery, state: FSMContext):
    reg_id = callback.data.split(':')[1]
    num_persons = await get_reg_persons_reg_id(reg_id)
    text = [
        'Введите актуальное количество человек или 0 (ноль) для удаления брони. Сейчас запись на',
        f'{num_persons["number_persons"]} человек'
            ]
    keyboard = home_kb()
    async with state.proxy() as data:
        data['reg_id'] = reg_id
    await FSMEvent.edit_reg.set()
    await callback.message.answer(' '.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def edit_registration_finish(message: Message, state: FSMContext):
    async with state.proxy() as data:
        reg_id = data.as_dict()['reg_id']
    if message.text.isdigit():
        if int(message.text) == 0:
            await delete_registration_reg_id_sql(reg_id)
        else:
            await edit_persons_reg_id_sql(reg_id, message.text)
        text = 'Запись изменена/удалена'
    else:
        text = 'Вы ввели не число. Попробуйте снова'
    keyboard = home_kb()
    await message.answer(text, reply_markup=keyboard)



async def delete_event(callback: CallbackQuery):
    text = '⚠️ ВНИМАНИЕ! Мероприятие будет безвозвратно удалено вместе со всеми записями. Восстановить будет невозможно'
    keyboard = delete_event_kb()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def accept_del_event(callback: CallbackQuery):
    text = [
        'В таком случае напишите послание клиентам, которые записались на мероприятие. Оно будет разослано, а',
        'мероприятие удалено как только Вы отправите это сообщение'
    ]
    keyboard = home_kb()
    await FSMEvent.delete_event.set()
    await callback.message.answer('\n'.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def deleting_finish(message: Message, state: FSMContext):
    async with state.proxy() as data:
        event_id = data.as_dict()['event_id']
    event_dict = await get_event_id_sql(event_id)
    user_list = await get_event_users_sql(event_id)
    event_title = event_dict['title']
    event_dtime = get_rus_dtime(event_dict["dtime"], 'date')
    await delete_event_sql(event_id)
    await delete_reg_event_sql(event_id)
    count = 0
    for user in user_list:
        user_id = user['user_id']
        try:
            await bot.send_message(chat_id=user_id, text=message.text)
            count += 1
        except:
            pass
    text_admin = f'Мероприятие {event_title} на {event_dtime} успешно удалено. Разослали {count} из {len(user_list)}'
    keyboard_admin = home_kb()
    await message.answer(text_admin, reply_markup=keyboard_admin)



async def get_event_list(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        event_id = data.as_dict()['event_id']
    await create_csv(event_id)
    doc_path = f'{os.getcwd()}/event_list.csv'
    await bot.send_document(chat_id=admin_group, document=open(doc_path, 'rb'))
    await bot.answer_callback_query(callback.id)


async def mailing(callback: CallbackQuery):
    text = [
        'Отправьте сюда текст рассылки. Он будет разослан всем пользователям, зарегистрированным в боте. Можно',
        'прикрепить картинку или видео'
    ]
    keyboard = home_kb()
    await FSMEvent.mailing.set()
    await callback.message.answer(' '.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def send_mailing_txt(message: Message):
    user_list = await get_users_sql()
    count = 0
    for user in user_list:
        user_id = user['user_id']
        try:
            await bot.send_message(user_id, message.text)
            count += 1
        except:
            pass
    text_admin = f'Разослали {count} пользователям из {len(user_list)}'
    keyboard_admin = home_kb()
    await FSMEvent.home.set()
    await message.answer(text_admin, reply_markup=keyboard_admin)


async def send_mailing_media(message: Message):
    text_user = message.caption
    user_list = await get_users_sql()
    count = 0
    for user in user_list:
        user_id = user['user_id']
        try:
            if len(message.photo) != 0:
                photo = message.photo[0].file_id
                await bot.send_photo(user_id, photo, caption=text_user)
                count += 1
            if message.video is not None:
                video = message.video.file_id
                await bot.send_video(user_id, video, caption=text_user)
                count += 1
        except:
            pass
    text_admin = f'Разослали {count} пользователям из {len(user_list)}'
    keyboard_admin = home_kb()
    await FSMEvent.home.set()
    await message.answer(text_admin, reply_markup=keyboard_admin)



def register_admin(dp: Dispatcher):
    error_states = [FSMEvent.title, FSMEvent.dtime, FSMEvent.capacity, FSMEvent.location, FSMEvent.description]
    dp.register_message_handler(admin_start_msg, commands=["start"], state="*", chat_id=admin_group)
    dp.register_message_handler(create_event_title, state=FSMEvent.title, content_types='text', chat_id=admin_group)
    dp.register_message_handler(create_event_dtime, state=FSMEvent.dtime, content_types='text', chat_id=admin_group)
    dp.register_message_handler(create_event_capacity, state=FSMEvent.capacity, content_types='text',
                                chat_id=admin_group)
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
    dp.register_message_handler(answer_user_finish, state=FSMEvent.answer, content_types='text', chat_id=admin_group)
    dp.register_message_handler(manual_reg_persons, state=FSMEvent.persons, content_types='text', chat_id=admin_group)
    dp.register_message_handler(manual_reg_nickname, state=FSMEvent.nickname, content_types='text', chat_id=admin_group)
    dp.register_message_handler(edit_registration_finish, state=FSMEvent.edit_reg, content_types='text',
                                chat_id=admin_group)
    dp.register_message_handler(send_mailing_txt, state=FSMEvent.mailing, content_types='text', chat_id=admin_group)
    dp.register_message_handler(send_mailing_media, state=FSMEvent.mailing, content_types=['photo', 'video'],
                                chat_id=admin_group)
    dp.register_message_handler(deleting_finish, state=FSMEvent.delete_event, content_types='text', chat_id=admin_group)


    dp.register_callback_query_handler(admin_start_clb, lambda x: x.data == 'home', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(admin_event_menu, lambda x: x.data == 'events', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(create_event, lambda x: x.data == 'create_event', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(public_event, lambda x: x.data == 'public', state=FSMEvent.description,
                                       chat_id=admin_group)
    dp.register_callback_query_handler(edit_desc, lambda x: x.data == 'edit_desc', state=FSMEvent.description,
                                       chat_id=admin_group)
    dp.register_callback_query_handler(edit_event_dtime, lambda x: x.data == 'edit_date', state=FSMEvent.description,
                                       chat_id=admin_group)
    dp.register_callback_query_handler(show_tables, lambda x: x.data == 'tables', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(new_tables, lambda x: x.data == 'edit_tables', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(answer_user_start, lambda x: x.data.split(':')[0] == 'answer', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(show_events, lambda x: x.data == 'get_events', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(event_info, lambda x: x.data.split(':')[0] == 'event', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(manual_reg_start, lambda x: x.data == 'manual_reg', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(manual_reg_wish, lambda x: x.data.split(':')[0] == 'wish', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(registration_finish, lambda x: x.data == 'accept_reg', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(edit_registration_start, lambda x: x.data == 'manual_edit', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(edit_registration, lambda x: x.data.split(':')[0] == 'reg_id', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(delete_event, lambda x: x.data == 'delete_event', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(accept_del_event, lambda x: x.data == 'delete_event_accept', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(get_event_list, lambda x: x.data == 'reg_list', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(mailing, lambda x: x.data == 'mailing', state='*', chat_id=admin_group)