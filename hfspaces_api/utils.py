"""Utility functions for the hfspaces_api"""
import itertools
import random
import os
import requests

def float_convert(x, base=35):
    """To create a random hash, converts a number to base of 36"""
    fexps = itertools.count(-1, -1)
    def exp_gen(x, base, exponents):
        for each in exponents:
            digit   = int(x // (base ** each))
            x       = x - digit * (base ** each)
            yield digit
            if x == 0 and e < 0:
                break

    return exp_gen(x - int(x), base, fexps)

def create_hash():
    """Creates a random hash of 11 characters"""
    conversion_map = '0123456789abcdefghijklmnopqrstuvwxyz'
    random_number = random.random()
    gen = float_convert(random_number, 36)
    str_hash = ''.join([conversion_map[next(gen)] for _ in range(11)])
    return str_hash


def download_app(app_url, branch='main', app_path='app.py'):
    '''downloads the given file'''
    full_path = os.path.join(app_url, 'raw', branch, app_path)
    out = None
    try:
        out = requests.get(full_path, timeout=10).text
    except Exception as err:
        raise RuntimeError(
            f'The following path cannot be downloaded : {full_path}') from err
    return out
