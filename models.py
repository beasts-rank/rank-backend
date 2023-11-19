from pydantic import BaseModel


class BeastMetaModel(BaseModel):
    percentage: float = 0.0
    description: str = ''

class BeastSourceModel(BeastMetaModel):
    name: str
