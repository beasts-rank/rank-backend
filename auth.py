import os
from math import inf
from datetime import datetime, timedelta
from pyotp import TOTP
from ast import literal_eval
from typing import Sequence

from itsdangerous import TimedSerializer

from rng_crypto import RNGCrypto
from base64 import b85encode

serializer = TimedSerializer(os.getenv("SECRET_KEY"), salt="SALTED")
totp = TOTP(os.getenv("SECRET_KEY"))

ADMIN_NAMES = literal_eval(os.getenv("ADMIN_NAMES"))
if not isinstance(ADMIN_NAMES, Sequence):
    raise ValueError("Invalid environment variable ADMIN_NAMES")


def verify_admin_password(name: str, password: str):
    if name not in ADMIN_NAMES:
        raise ValueError("Invalid admin name")

    return b85encode(RNGCrypto(int(os.getenv("SEED"))).encrypt(name.encode('u8'))) == password.encode()


def get_admin_flag():
    return serializer.dumps({"is_admin": True}, )


def verify_admin_flag(flag: str, max_age: timedelta | int = None):
    max_age = inf if not max_age else max_age
    max_age = max_age.total_seconds() if isinstance(max_age, timedelta) else max_age

    return serializer.loads(flag, max_age)
