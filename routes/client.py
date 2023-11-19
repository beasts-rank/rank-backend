from ipaddress import ip_address
from uuid import UUID

from helper import response
from fastapi import APIRouter, Request

from manager import bc
from models import BeastMetaModel
from structures import Beast

router = APIRouter(prefix="/api/client", tags=['clientApi'])


@router.get('/hello')
async def hello():
    return response(msg='Hello World!')


@router.get("/beasts")
async def get_beasts(p: int, cnt: int = 8):
    return response(data=tuple(bc.paged_beasts(p, cnt)))


@router.get("/beasts/{uuid}")
async def get_beast(uuid: UUID):
    return response(data=bc.get_beast(uuid))


@router.get("/beasts/{uuid}/like")
@router.post("/beasts/{uuid}/like")
async def ch_beast_like(uuid: UUID, request: Request):
    if request.method == 'GET':
        return response(data={
            'like': ip_address(request.client.host) in bc.get_beast(uuid).like
        })

    beast = bc.get_beast(uuid)
    stats = beast.ch_like(ip_address(request.client.host))
    return response(msg='Success', data={
        'like': stats,
        'count': len(beast.meta.like)
    })


@router.get("/beasts/{uuid}/dislike")
@router.post("/beasts/{uuid}/dislike")
async def ch_beast_dislike(uuid: UUID, request: Request):
    if request.method == 'GET':
        return response(data={
            'dislike': ip_address(request.client.host) in bc.get_beast(uuid).dislike
        })

    beast = bc.get_beast(uuid)
    stats = beast.ch_dislike(ip_address(request.client.host))
    return response(msg='Success', data={
        'dislike': stats,
        'count': len(beast.meta.dislike)
    })
