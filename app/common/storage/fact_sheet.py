import csv
import functools

import boto3

from common import envs

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
