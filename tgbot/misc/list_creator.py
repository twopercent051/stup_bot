import csv
import os

from tgbot.models.db_connector import get_list_sql, get_event_id_sql
from tgbot.misc.datetime_handler import get_rus_dtime

async def create_csv(event_id):
    event_dict = await get_event_id_sql(event_id)
    reg_list = await get_list_sql(event_id)
    event_dtime = get_rus_dtime(event_dict["dtime"], 'date')
    with open(f'{os.getcwd()}/event_list.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            ('Мероприятие:', event_dict['title'])
        )
        writer.writerow(
            ('Дата:', event_dtime)
        )
        writer.writerow(
            (' ')
        )
        writer.writerow(
            (
                'Стол',
                'Кол-во людей',
                'Место у сцены',
                'Юзернейм клиента'
            )
        )
    for reg in reg_list:
        table_name = reg['table_name']
        user_id = reg['user_id']
        if user_id == 0:
            table_name += ' *'
        persons = reg['number_persons']
        wish = reg['wish']
        place = None
        if wish == 'closer':
            place = 'Ближе'
        if wish == 'further':
            place = 'Дальше'
        if wish == 'no_diff':
            place = 'Без разницы'
        username = reg['nick_name']
        with open(f'{os.getcwd()}/event_list.csv', 'a', encoding='utf-8-sig') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerow(
                (
                    table_name,
                    persons,
                    place,
                    username
                )
            )
    with open(f'{os.getcwd()}/event_list.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (' ')
        )
        writer.writerow(
            (' ')
        )
        writer.writerow(
            ('Символ * после названия стола означает, что клиент добавлен администратором',)
        )


