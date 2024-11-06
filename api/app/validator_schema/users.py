from pydantic.main import BaseModel
from enum import Enum


class TRole(str, Enum):
    admin = "admin"
    user = "user"


class TSignup(BaseModel):
    username: str
    password: str


class TSignin(BaseModel):
    username: str
    password: str


class TCreateAvatar(BaseModel):
    imageUrl: str
    name: str
