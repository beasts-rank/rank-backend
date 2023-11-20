from typing import Any

from pydantic import BaseModel


class BeastMetaModel(BaseModel):
    percentage: float = 0.0
    description: str = ''

class BeastSourceModel(BeastMetaModel):
    name: str


class Response(BaseModel):
    code: int = 200
    msg: str = ""
    data: Any

class AdminWelcomeModel(Response):
    data: Beasts
