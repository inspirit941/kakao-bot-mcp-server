from typing import Optional

from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    expires_in: int
    scope: Optional[str] = None
    id_token: Optional[str] = None
