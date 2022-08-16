import logging

from common import envs

log_level = logging.getLevelName(envs.LOG_LEVEL)

logger = logging.getLogger()
logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)
logger.setLevel(log_level)


def info(msg, *args, **kwargs):
    logging.info(msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    logging.debug(msg, *args, **kwargs)


def warn(msg, *args, **kwargs):
    logging.warning(msg, *args, **kwargs)
