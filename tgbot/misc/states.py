from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMEvent(StatesGroup):
    home = State()
    title = State()
    date = State()
    time = State()
    location = State()
    picture = State()
    description = State()
    tables = State()


class FSMUser(StatesGroup):
    home = State()



