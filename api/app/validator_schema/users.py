from enum import Enum

from pydantic.main import BaseModel


class TRole(str, Enum):
    admin = "admin"
    user = "user"


class TSignup(BaseModel):
    username: str
    password: str
    type: TRole


class TSignin(BaseModel):
    username: str
    password: str
