import datetime

from common import envs


def now_iso():
    return datetime.datetime.now().isoformat()


def now_timestamp():
    return int(datetime.datetime.now().timestamp())


def ttl():
    dt = datetime.datetime.now() + datetime.timedelta(days=envs.DYNAMODB_TTL_DAYS)
    return int(dt.timestamp())


def remaining_seconds(timer_seconds: int, timer_start: int):
    if timer_seconds and timer_start:
        elapsed_seconds = now_timestamp() - timer_start
        return max(timer_seconds - elapsed_seconds, 0)
