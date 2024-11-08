from pydantic.main import BaseModel


class TCreateElement(BaseModel):
    imageUrl: str
    height: int
    width: int
    static: bool
    name:str


class TUpdateElement(BaseModel):
    id: str
    imageUrl: str


class TUpdateElementBody(BaseModel):
    imageUrl: str
