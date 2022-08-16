import datetime

from common import envs


def now_iso():
    return datetime.datetime.now().isoformat()


def now_timestamp():
    return int(datetime.datetime.now().timestamp())


def ttl():
    dt = datetime.datetime.now() + datetime.timedelta(days=envs.DYNAMODB_TTL_DAYS)
    return int(dt.timestamp())
