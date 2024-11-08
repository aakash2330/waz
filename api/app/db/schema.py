import uuid

from sqlmodel import Field, Relationship, SQLModel
from validator_schema.users import TRole


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True)
    password: str
    avatarId: str | None
    type: TRole
    spaces: list["Space"] = Relationship(back_populates="creator")


class Element(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True)
    imageUrl: str = Field(unique=True)
    width: int = Field(default=1)
    height: int = Field(default=1)
    static: bool
    space_elements: list["SpaceElement"] = Relationship(back_populates="element")


class Avatar(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    imageUrl: str = Field(unique=True)
    name: str = Field(unique=True)


class Space(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    thumbnail: str | None = Field(default=1)
    name: str = Field(unique=True)
    width: int = Field(default=1)
    height: int = Field(default=1)
    creatorId: uuid.UUID = Field(foreign_key="user.id")
    creator: User | None = Relationship(back_populates="spaces")
    spaceElements: list["SpaceElement"] = Relationship(back_populates="space")


class SpaceElement(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    x: int
    y: int
    space_id: uuid.UUID = Field(foreign_key="space.id")
    space: Space | None = Relationship(back_populates="spaceElements")
    element_id: uuid.UUID = Field(foreign_key="element.id")
    element: Element = Relationship(back_populates="space_elements")
