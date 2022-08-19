import csv
import functools
from random import Random
from typing import List

import boto3

from common import envs
from common.storage.str_util import recover_decode_utf8

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
    end_bytes = start_bytes + range_bytes
    print(f'Reading range {start_bytes}-{end_bytes}')

    response = _s3().get_object(
        Bucket=envs.CONTENT_BUCKET,
        Key=f'{QUIZ_DIR}/{key}',
        Range=f'bytes={start_bytes}-{end_bytes}'
    )
    body = recover_decode_utf8(response['Body'].read())
    lines = body.splitlines(True)
    reader = csv.DictReader(lines[1:-1], fieldnames=fieldnames)
    return list(reader)


if __name__ == '__main__':
    print('Hi')

    rows = load_sample_rows('efremova.csv', ['word', 'description'])
    for row in rows:
        print(row)

    # bt = b'12345'
    # print(bt[1:-2])
