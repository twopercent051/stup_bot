from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMEvent(StatesGroup):
    home = State()
    title = State()
    dtime = State()
    capacity = State()
    location = State()
    picture = State()
    description = State()
    tables = State()
    answer = State()
    persons = State()
    nickname = State()
    wish = State()
    edit_reg = State()
    delete_event = State()
    mailing = State()


class FSMUser(StatesGroup):
    home = State()
    create_reg = State()
    number_persons = State()
    wish = State()
    edit_reg = State()
    support = State()



