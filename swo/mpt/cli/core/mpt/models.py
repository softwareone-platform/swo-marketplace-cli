from pydantic import BaseModel


class Account(BaseModel):
    id: str
    name: str
    type: str


class Token(BaseModel):
    id: str
    account: Account
