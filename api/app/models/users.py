import uuid
from sqlmodel import Field, SQLModel
from validator_schema.users import TRole


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True)
    password: str
    avatarId: str | None
    type: TRole
