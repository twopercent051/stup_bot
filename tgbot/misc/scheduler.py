import time

from tgbot.models.db_connector import *
from create_bot import scheduler

async def user_counter_scheduler():
    event_list = await get_user_events_sql()
    now = time.time()
    for event in event_list:
        event_dt = event['dtime']
        event_id = event['id']

        if event_dt < now:
            await edit_event_status_sql(event_id)





def scheduler_jobs():
    scheduler.add_job(user_counter_scheduler, "interval", minutes=62)
    # pass