from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    hub_id: Optional[str] = None
    preferred_language: Optional[str] = "en"

