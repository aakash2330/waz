import uuid

from sqlmodel import Field, Relationship, SQLModel
from validator_schema.users import TRole


class Element(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True)
    imageUrl: str = Field(unique=True)
    width: int = Field(default=1)
    height: int = Field(default=1)
    static: bool
    space_elements: list["SpaceElement"] = Relationship(
        back_populates="element", sa_relationship_kwargs={"lazy": "joined"}
    )


class Avatar(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    imageUrl: str = Field(unique=True)
    name: str = Field(unique=True)
    users: list["User"] = Relationship(
        back_populates="avatar", sa_relationship_kwargs={"lazy": "joined"}
    )


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True)
    password: str
    avatarId: uuid.UUID | None = Field(default=None, foreign_key="avatar.id")
    avatar: Avatar = Relationship(
        back_populates="users", sa_relationship_kwargs={"lazy": "joined"}
    )
    type: TRole
    spaces: list["Space"] = Relationship(
        back_populates="creator", sa_relationship_kwargs={"lazy": "joined"}
    )


class Space(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    thumbnail: str | None = Field(default=None)
    name: str = Field(unique=True)
    width: int = Field(default=1)
    height: int = Field(default=1)
    creatorId: uuid.UUID = Field(foreign_key="user.id")
    creator: User | None = Relationship(
        back_populates="spaces", sa_relationship_kwargs={"lazy": "joined"}
    )
    spaceElements: list["SpaceElement"] = Relationship(
        back_populates="space", sa_relationship_kwargs={"lazy": "joined"}
    )


class SpaceElement(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True)
    x: int
    y: int
    space_id: uuid.UUID = Field(foreign_key="space.id")
    space: Space | None = Relationship(
        back_populates="spaceElements", sa_relationship_kwargs={"lazy": "joined"}
    )
    element_id: uuid.UUID = Field(foreign_key="element.id")
    element: Element = Relationship(
        back_populates="space_elements", sa_relationship_kwargs={"lazy": "joined"}
    )
