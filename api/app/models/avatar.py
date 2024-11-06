import uuid
from sqlmodel import Field, SQLModel


class Avatar(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    imageUrl: str = Field(unique=True)
    name: str = Field(unique=True)
