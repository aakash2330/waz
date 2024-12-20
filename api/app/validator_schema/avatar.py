from pydantic.main import BaseModel


class TCreateAvatar(BaseModel):
    imageUrl: str
    name: str


class TUpdateMetadata(BaseModel):
    avatarId: str
