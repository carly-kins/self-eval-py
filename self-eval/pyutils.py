#!/usr/bin/env python3

from subprocess import check_output, CalledProcessError
from datetime import datetime, timezone

FORMAT = '%Y-%m-%d'

def fzf(input_items, fzf_args_str=''):
    input_bytes = '\n'.join(input_items).encode('utf-8')
    try:
        output = check_output(f'fzf {fzf_args_str}', shell=True, input=input_bytes)
    except CalledProcessError as e:
        # fzf will return 130 if nothing is chosen; output will still be empty.
        output = e.output
    return output.decode('utf-8').strip()

def now_utc():
    return datetime.strftime(datetime.now(timezone.utc), f'{FORMAT} %H:%M:%S')

def strftime_format(value):
    try:
        datetime.strptime(value, FORMAT)
    except ValueError:
        return False
    return True