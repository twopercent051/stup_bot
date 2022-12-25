from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.misc.datetime_handler import get_rus_dtime

def admin_mainmenu_kb():
    events_button = InlineKeyboardButton(text='📂 Мероприятия', callback_data='events')
    tables_button = InlineKeyboardButton(text='🪑 Столы', callback_data='tables')
    mailing_button = InlineKeyboardButton(text='✉️ Рассылка', callback_data='mailing')
    keyboard = InlineKeyboardMarkup(row_width=1).add(events_button, tables_button, mailing_button)
    return keyboard

def user_mainmenu_kb():
    record_button = InlineKeyboardButton(text='Забронировать стол', callback_data='record')
    edit_reg_button = InlineKeyboardButton(text='Редактировать мои записи', callback_data='edit_reg')
    support_button = InlineKeyboardButton(text='Оставить обращение', callback_data='support')
    keyboard = InlineKeyboardMarkup(row_width=1).add(record_button, edit_reg_button, support_button)
    return keyboard


def admin_event_menu_kb():
    create_event_button = InlineKeyboardButton(text='📂 Создать мероприятие', callback_data='create_event')
    get_events_button = InlineKeyboardButton(text='🎃 Посмотреть мероприятия', callback_data='get_events')
    keyboard = InlineKeyboardMarkup(row_width=1).add(create_event_button, get_events_button)
    return keyboard

def home_kb():
    home_button = InlineKeyboardButton(text='🏠 В главное меню', callback_data='home')
    keyboard = InlineKeyboardMarkup(row_width=1).add(home_button)
    return keyboard

def public_event_kb():
    home_button = InlineKeyboardButton(text='🏠 В главное меню', callback_data='home')
    accept_button = InlineKeyboardButton(text='✅ Опубликовать', callback_data='public')
    keyboard = InlineKeyboardMarkup(row_width=1).add(accept_button, home_button)
    return keyboard

def incorrect_date_kb():
    home_button = InlineKeyboardButton(text='🏠 В главное меню', callback_data='home')
    edit_date_button = InlineKeyboardButton(text='Редактировать дату', callback_data='edit_date')
    keyboard = InlineKeyboardMarkup(row_width=1).add(home_button, edit_date_button)
    return keyboard

def too_long_desc_kb():
    home_button = InlineKeyboardButton(text='🏠 В главное меню', callback_data='home')
    edit_desc_button = InlineKeyboardButton(text='Редактировать описание', callback_data='edit_desc')
    keyboard = InlineKeyboardMarkup(row_width=1).add(home_button, edit_desc_button)
    return keyboard

def edit_tables_kb():
    home_button = InlineKeyboardButton(text='🏠 В главное меню', callback_data='home')
    edit_desc_button = InlineKeyboardButton(text='Редактировать столы', callback_data='edit_tables')
    keyboard = InlineKeyboardMarkup(row_width=1).add(home_button, edit_desc_button)
    return keyboard


def events_kb(events, is_admin):
    keyboard = InlineKeyboardMarkup(row_width=1)
    home_button = InlineKeyboardButton(text='🏠 В главное меню', callback_data='home')
    for event in events:
        id = event['id']
        title = event['title']
        date = get_rus_dtime(event['dtime'], 'date')
        status = event['status']
        if is_admin:
            if status == 'upcoming':
                emodji = '🟩'
            else:
                emodji = '🟥'
        else:
            emodji = ''
        button = InlineKeyboardButton(text=f'{emodji} {title}||{date}', callback_data=f'event:{id}')
        keyboard.add(button)
    keyboard.add(home_button)
    return keyboard


def reg_list_kb(registrations):
    keyboard = InlineKeyboardMarkup(row_width=1)
    home_button = InlineKeyboardButton(text='🏠 В главное меню', callback_data='home')
    for reg in registrations:
        reg_id = reg['id']
        username = reg['nick_name']
        table_name = reg['table_name']
        button = InlineKeyboardButton(text=f'{username} || {table_name}', callback_data=f'reg_id:{reg_id}')
        keyboard.add(button)
    keyboard.add(home_button)
    return keyboard



def wish_kb():
    closer_button = InlineKeyboardButton(text='Ближе к сцене!', callback_data='wish:closer')
    further_button = InlineKeyboardButton(text='Подальше от сцены!', callback_data='wish:further')
    no_diff_button = InlineKeyboardButton(text='Мне всё равно', callback_data='wish:no_diff')
    keyboard = InlineKeyboardMarkup(row_width=1).add(closer_button, further_button, no_diff_button)
    return keyboard

def accept_registaration_kb():
    accept_button = InlineKeyboardButton(text='Да! Всё верно', callback_data='accept_reg')
    refuse_button = InlineKeyboardButton(text='Нет, всё не так. Давай заново', callback_data='refuse_reg')
    keyboard = InlineKeyboardMarkup(row_width=1).add(accept_button, refuse_button)
    return keyboard


def edit_registration_kb():
    edit_reg_button = InlineKeyboardButton(text='Редактировать мои записи', callback_data='edit_reg')
    home_button = InlineKeyboardButton(text='🏠 В главное меню', callback_data='home')
    keyboard = InlineKeyboardMarkup(row_width=1).add(edit_reg_button, home_button)
    return keyboard


def edit_reg_menu_kb():
    edit_persons_button = InlineKeyboardButton(text='Количество человек поменялось', callback_data='edit_persons')
    delete_reg_button = InlineKeyboardButton(text='Планы поменялись, мы не придём', callback_data='del_reg')
    home_button = InlineKeyboardButton(text='🏠 В главное меню', callback_data='home')
    keyboard = InlineKeyboardMarkup(row_width=1).add(edit_persons_button, delete_reg_button, home_button)
    return keyboard


def answer_kb(user_id):
    answer_button = InlineKeyboardButton(text='Ответить', callback_data=f'answer:{user_id}')
    keyboard = InlineKeyboardMarkup(row_width=1).add(answer_button)
    return keyboard


def admin_event_kb():
    manual_add_button = InlineKeyboardButton(text='Ручная регистрация зрителя', callback_data='manual_reg')
    manual_edit_button = InlineKeyboardButton(text='Редактировать запись', callback_data='manual_edit')
    delete_button = InlineKeyboardButton(text='Удалить мероприятие!', callback_data='delete_event')
    reg_list_button = InlineKeyboardButton(text='Посадочный лист', callback_data='reg_list')
    keyboard = InlineKeyboardMarkup(row_width=1).add(manual_add_button, manual_edit_button, delete_button,
                                                     reg_list_button)
    return keyboard


def delete_event_kb():
    delete_event_button = InlineKeyboardButton(text='Да, удаляем', callback_data='delete_event_accept')
    home_button = InlineKeyboardButton(text='🏠 В главное меню', callback_data='home')
    keyboard = InlineKeyboardMarkup(row_width=1).add(delete_event_button, home_button)
    return keyboard
