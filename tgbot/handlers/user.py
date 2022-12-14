from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.keyboards.inline import *
from tgbot.misc.states import FSMUser
from tgbot.models.redis_connector import *

async def user_start(message: Message):
    text = [
        'Здравствуйте! Это приветственное сообщение, его нужно отредактировать. Тут можно писать <b>жирным</b>,',
        '<i>курсивом</i>, <u>подчёркнутым</u>, <b><i>а также любыми</i></b> <u><i>комбинациями</i></u>. Ещё можно',
        'добавить эмодзи 🇬🇧.',
        '\n',
        'А теперь нажмите на интересующую кнопку!'
    ]
    keyboard = user_mainmenu_kb()
    await FSMUser.home.set()
    await message.answer(' '.join(text), reply_markup=keyboard)
    

async def true(message: Message):
    status = await get_working()
    await message.answer(status)



def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(true, commands=["true"], state="*")

