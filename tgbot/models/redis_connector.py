import redis

r = redis.Redis()

def redis_start():
    r.set('is_working', 'True')

async def toggle_working():
    status = r.get('is_working').decode('utf-8')
    if status == 'True':
        r.set('is_working', 'False')
    else:
        r.set('is_working', 'True')

async def get_working():
    status = r.get('is_working').decode('utf-8')
    return status

# r.mset({'Croatia': 'Zagreb', 'Bahamas': 'Nassau'})