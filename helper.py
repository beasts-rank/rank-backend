import warnings
from dataclasses import is_dataclass, asdict
from datetime import datetime
from functools import wraps
from json import dumps, loads
from typing import Any, Mapping, Callable
from uuid import UUID

from fastapi import Response
from pydantic import BaseModel

template = {"code": 200, 'msg': '', 'data': None}


def default(obj: Any):
    if callable(getattr(obj, 'to_json', None)):
        return obj.to_json()

    if isinstance(obj, UUID):
        return str(obj)

    if is_dataclass(obj):
        return asdict(obj)

    if isinstance(obj, BaseModel):
        return obj.model_dump()

    if isinstance(obj, datetime):
        return obj.timestamp()

    if isinstance(obj, set):
        return tuple(obj)

    if hasattr(obj, '__dict__'):
        warnings.warn(f"obj {repr(obj)} is covert through __dict__")
        return obj.__dict__

    raise ValueError(f"obj {repr(obj)} is not parsable")


def response_default(obj: Any):
    if callable(getattr(obj, 'to_public_json', None)):
        return obj.to_public_json()

    if isinstance(obj, UUID):
        return str(obj)

    if is_dataclass(obj):
        return asdict(obj)

    if isinstance(obj, BaseModel):
        return obj.model_dump()

    if isinstance(obj, datetime):
        return obj.timestamp()

    if callable(getattr(obj, 'to_json', None)):
        return obj.to_json()

    return repr(obj)


def response(_headers: Mapping[str, Any] = None, **kwargs):
    json = template.copy()
    json.update(kwargs)
    return Response(
        dumps(json, default=response_default),
        status_code=json['code'],
        media_type='application/json',
        headers=_headers
    )


def debounce(seconds, default_factory: Callable = lambda *args, **kwargs: None):
    """Decorator ensures function that can only be called once every `s` seconds.
    """
    import time

    def decorate(f):
        t = 0

        @wraps(f)
        def wrapped(*args, **kwargs):
            nonlocal t
            t_ = time.time_ns()
            if t is None or t_ - t >= seconds:
                result = f(*args, **kwargs)
                t = time.time_ns()
                return result

            return default_factory(*args, **kwargs)

        return wrapped

    return decorate
