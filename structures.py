from dataclasses import dataclass, field, is_dataclass, asdict
from datetime import datetime
from typing import TypeAlias, Any, Self
from uuid import UUID, uuid4
from ipaddress import IPv4Address, IPv6Address, ip_address

from time import time as now_timestamp

from pydantic import BaseModel

IPAddress: TypeAlias = IPv4Address | IPv6Address

JSON: TypeAlias = dict[str, Any]


@dataclass
class BeastMeta:
    description: str
    like: set[IPAddress]
    dislike: set[IPAddress]
    created_at: datetime

    @classmethod
    def from_json(cls, data: JSON) -> Self:
        description = data.get('description')
        like = set(map(ip_address, data.get('like', ())))
        dislike = set(map(ip_address, data.get('dislike', ())))
        created_at = datetime.fromtimestamp(data.get('created_at', now_timestamp()))
        return cls(description, like, dislike, created_at)


class Beast:
    def __init__(self, name: str, percentage: int, uuid: UUID = None, meta: BeastMeta | dict[str, Any] = None):
        if not meta:
            meta = BeastMeta('', set(), set(), datetime.now())
        if isinstance(meta, dict):
            meta = BeastMeta.from_json(meta)

        self.name = name
        self.percentage = percentage
        self.uuid = uuid
        self.meta = meta

    def __repr__(self):
        return f"{type(self).__name__}(uuid={self.uuid}, name={self.name}, meta={repr(self.meta)})"

    def __hash__(self):
        return self.uuid.int

    def __eq__(self, other):
        if isinstance(other, Beast):
            return self.uuid == other.uuid
        return False

    def to_public_json(self) -> JSON:
        return {
            'name': self.name,
            'percentage': self.percentage,
            'description': self.meta.description,
            'created_at': self.meta.created_at
        }

    def to_json(self) -> JSON:
        return self.__dict__

    @classmethod
    def from_public_json(cls, json: JSON) -> Self:
        json['meta'] = json
        json.setdefault('uuid', str(uuid4()))
        return cls.from_json(json)

    @classmethod
    def from_json(cls, json: JSON) -> Self:
        name = json.get('name')
        percentage = int(json.get('percentage'))
        uuid = UUID(json.get('uuid'))
        return cls(name, percentage, uuid, json.get('meta'))

    def ch_like(self, ip: IPAddress):
        self.meta.like ^= {ip, }
        self.meta.dislike.discard(ip)
        return self.meta.like

    def ch_dislike(self, ip: IPAddress):
        self.meta.dislike ^= {ip, }
        self.meta.like.discard(ip)
        return self.meta.dislike


@dataclass
class Config:
    beasts: dict[UUID, Beast] = field(default_factory=dict)
    max_pagesize: int = 35

    def to_json(self):
        beasts = tuple(self.beasts.values())
        return {
            'beasts': beasts,
            'max_pagesize': self.max_pagesize
        }

    @classmethod
    def from_json(cls, json: JSON) -> Self:
        raw_beasts = json.get('beasts', ())
        beasts = map(
            Beast.from_json,
            raw_beasts.values() if isinstance(raw_beasts, dict) else raw_beasts
        )
        beasts_map = dict((beast.uuid, beast) for beast in beasts)
        max_pagesize = json.get('max_pagesize', 35)
        return cls(beasts_map, max_pagesize)
