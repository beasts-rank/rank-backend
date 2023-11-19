from typing import Annotated
from uuid import UUID

from fastapi.security import HTTPBasic, HTTPBasicCredentials

from auth import verify_admin_flag, totp, ADMIN_NAMES, verify_admin_password
from helper import response
from fastapi import APIRouter, Depends, HTTPException, Header, Request

from manager import bc
from models import BeastMetaModel, BeastSourceModel
from structures import Beast
import random

security = HTTPBasic()


async def check_auth(
        request: Request,
        x_auth: Annotated[str | None, Header()] = None,
        credentials: Annotated[HTTPBasicCredentials, Depends(security)] = None
):
    if not credentials and not x_auth:
        raise HTTPException(401, 'Unauthorized', headers={"WWW-Authenticate": "Basic"})

    if x_auth:
        return getattr(verify_admin_flag(x_auth), 'user', True)

    if not credentials.username:
        raise HTTPException(401, "Unauthorized")

    if credentials.username == "__otp__":
        if not totp.verify(credentials.password):
            raise HTTPException(401, f"Access denied")

    if credentials.username == 'anonymous':
        raise HTTPException(401, f'?')

    if verify_admin_password(credentials.username, credentials.password):
        return credentials.username

    raise HTTPException(401, f'Forbidden')


router = APIRouter(
    prefix="/api/admin",
    tags=['adminApi'],
    dependencies=(Depends(check_auth),)
)


@router.get("/test")
@router.get("/welcome")
async def test():
    return response(msg=random.choice([
        "Ogali, Dokutah",
        "Welcome, my master desu!",
        "Hellow",
        "Hello World!"
    ]))


@router.post("/beasts/")
@router.put("/beasts/")
async def put_beast(beast: BeastSourceModel):
    beast = bc.add_beast(Beast.from_public_json(beast.model_dump()))
    return response(msg='Success', data={
        'uuid': beast.uuid
    })


@router.put("/beasts/{uuid}")
@router.patch("/beasts/{uuid}")
async def patch_beast(uuid: UUID, beast: BeastMetaModel):
    bc.patch_beast(uuid, beast.model_dump())
    return response(msg='Success')
