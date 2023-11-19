import importlib
import importlib.util
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, APIRouter, Request, HTTPException, Response
from itsdangerous import BadSignature, BadTimeSignature
from starlette.middleware.base import BaseHTTPMiddleware

from helper import response
from manager import cfg


def find_routers() -> list[APIRouter]:
    routers = []
    routes_dir = Path('./routes')
    for router_file in routes_dir.iterdir():
        if not router_file.is_file():
            continue
        if not router_file.suffix == '.py':
            continue

        spec = importlib.util.spec_from_file_location(router_file.name, router_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        router = getattr(module, 'router', None)
        if isinstance(router, APIRouter):
            routers.append(router)

    return routers


async def bad_sign_handler(req: Request, exc: BadSignature):
    return response(code=401, msg="invalid signature")


async def bad_time_handler(req: Request, exc: BadSignature):
    return response(code=401, msg="login expired")


async def base_handler(req: Request, exc: HTTPException):
    return response(code=exc.status_code, msg=exc.detail, _headers=exc.headers)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg.load()
    yield
    cfg.write()


async def auto_save(request: Request, call_next: Callable[[Request], Response]):
    resp = await call_next(request)
    if request.method != 'GET':
        await cfg.debounced_write_async()
    return resp


def create_app() -> FastAPI:
    app = FastAPI(title="Beasts Rank Backend", lifespan=lifespan)
    app.add_middleware(BaseHTTPMiddleware, dispatch=auto_save)

    [app.include_router(router) for router in find_routers()]

    app.add_exception_handler(BadSignature, bad_sign_handler)
    app.add_exception_handler(BadTimeSignature, bad_time_handler)
    app.add_exception_handler(HTTPException, base_handler)

    return app
