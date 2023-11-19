from uuid import UUID

from fastapi import HTTPException


class BeastNotFoundError(ValueError, HTTPException):
    def __init__(self, uuid: UUID):
        HTTPException.__init__(
            self,
            400,
            detail=f"Beast(uuid={uuid}) is not exist"
        )
