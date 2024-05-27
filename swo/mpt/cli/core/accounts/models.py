from pydantic import BaseModel


class Account(BaseModel):
    id: str
    name: str
    type: str
    token: str
    token_id: str
    environment: str
    is_active: bool = False
