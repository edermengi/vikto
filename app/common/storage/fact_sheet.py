import csv
import functools
import logging
from random import Random
from typing import List

import boto3

from common import envs
from common.storage.str_util import recover_decode_utf8

log = logging.getLogger(__name__)

QUIZ_DIR = 'sheets'


@functools.cache
def _s3(_=''):
    return boto3.client('s3')


def load_rows(key: str):
    response = _s3().get_object(
        Bucket=envs.CONTENT_BUCKET,
        Key=f'{QUIZ_DIR}/{key}'
    )
    lines = response['Body'].read().decode('utf-8').splitlines(True)
    reader = csv.DictReader(lines)
    return list(reader)


@functools.cache
def _get_object_size_bytes(key: str):
    response = _s3().head_object(
        Bucket=envs.CONTENT_BUCKET,
        Key=f'{QUIZ_DIR}/{key}'
    )
    return response['ContentLength']


def load_sample_rows(key: str, fieldnames: List[str], range_bytes=10000):
    object_size = _get_object_size_bytes(key)
    start_bytes = Random().randint(0, object_size - range_bytes)
    end_bytes = min(start_bytes + range_bytes, object_size)
    log.info(f'Reading range {start_bytes}-{end_bytes} from {object_size}')

    response = _s3().get_object(
        Bucket=envs.CONTENT_BUCKET,
        Key=f'{QUIZ_DIR}/{key}',
        Range=f'bytes={start_bytes}-{end_bytes}'
    )
    body = recover_decode_utf8(response['Body'].read())
    lines = body.splitlines(True)
    reader = csv.DictReader(lines[1:-1], fieldnames=fieldnames)
    return list(reader)
