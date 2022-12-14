from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_mainmenu_kb():
    events_button = InlineKeyboardButton(text='🤡 Мероприятия', callback_data='events')
    tables_button = InlineKeyboardButton(text='🪑 Столы', callback_data='tables')
    keyboard = InlineKeyboardMarkup(row_width=1).add(events_button, tables_button)
    return keyboard

def user_mainmenu_kb():
    record_button = InlineKeyboardButton(text='Забронировать стол', callback_data='record')
    keyboard = InlineKeyboardMarkup(row_width=1).add(record_button)
    return keyboard


def admin_event_menu_kb():
    create_event_button = InlineKeyboardButton(text='🤡 Создать мероприятие', callback_data='create_event')
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
