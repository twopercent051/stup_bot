import datetime
import time


def get_datetime_stamp(date_string):
    now = time.time()
    try:
        date = datetime.datetime.strptime(date_string, "%d.%m.%Y %H:%M")
        time_stamp = datetime.datetime.timestamp(date)
        if time_stamp < now:
            return None
        else:
            return time_stamp
    except:
        return None



def get_rus_dtime(dt_timestamp, info):

    time_tuple = time.localtime(float(dt_timestamp))
    month_dict = {
        '1': 'января',
        '2': 'февраля',
        '3': 'марта',
        '4': 'апреля',
        '5': 'мая',
        '6': 'июня',
        '7': 'июля',
        '8': 'августа',
        '9': 'сентября',
        '10': 'октября',
        '11': 'ноября',
        '12': 'декабря',
    }
    try:
        month = str(time_tuple[1])
        minutes = '00' if time_tuple[4] == 0 else time_tuple[4]
        d = f'{time_tuple[2]} {month_dict[month]}'
        t = f'{time_tuple[3]}:{minutes}'
        if info == 'all':
            return f'{d} в {t}'
        if info == 'date':
            return d
        if info == 'time':
            return t
    except:
        return None


# tuple = (2022, 12, 7, 20, 00, 0)
# print(get_rus_dtime(tuple))