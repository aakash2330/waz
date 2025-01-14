import logging
from typing import Any

from fastapi.encoders import jsonable_encoder

from validator_schema.avatar import TUpdateMetadata

import bcrypt
import jwt
from sqlmodel import Session, select

from db.db import engine
from db.schema import Avatar, User
from validator_schema.users import TGetUserMetadata, TSignin, TSignup, TUserMetadata

logging.basicConfig(level=logging.DEBUG)


def add_user_to_db(data: TSignup) -> tuple[int, dict[str, str] | None]:
    with Session(engine) as session:
        query = select(User).where(User.username == data.username)
        userExists = session.exec(query).first()
        if userExists:
            raise ValueError("User Exists")

        hashedPassword = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode(
            "utf-8"
        )

        user = User(
            username=data.username,
            password=hashedPassword,
            type=data.type,
            avatarId=None,
        )

        session.add(user)
        session.commit()
        session.refresh(user)
        session.close()

    return 200, {"userId": str(user.id)}


def find_user_by_id(data: TSignin):
    with Session(engine) as session:
        query = select(User).where(User.username == data.username)
        foundUser = session.exec(query).first()

        if foundUser is None:
            raise ValueError(f"User with the username {data.username} doesn't exist ")

        if bcrypt.checkpw(
            data.password.encode("utf-8"), foundUser.password.encode("utf-8")
        ):
            return foundUser
        raise ValueError(f"Password Incorrect for the username {data.username} ")


def generate_jwt_token(data: User):
    payload: dict[str, Any] = data.model_dump(exclude={"password"})
    token = jwt.encode(jsonable_encoder(payload), "secret", algorithm="HS256")
    return str(token)


def user_sign_in(data: TSignin) -> tuple[int, dict[str, str] | None]:
    logging.info(
        f"getting user data for username -  {data.username} and comparing password"
    )
    user = find_user_by_id(data)

    logging.info("generating token for the user")

    token = generate_jwt_token(user)
    return 200, {"token": token}


def get_bulk_user_metadata(
    body: TGetUserMetadata,
) -> tuple[int, dict[str, list[TUserMetadata]] | None]:
    logging.info(f"getting meta data for users with id's {body.ids}")
    with Session(engine) as session:
        query = select(User).where(
            User.id.in_(body.ids)  # pyright: ignore[reportAttributeAccessIssue]
        )
        users = session.exec(query).unique().all()
        if not users:
            raise ValueError("Couldnt find users with the given ids")

        logging.info("converting found users to desired shape")
        usersList: list[TUserMetadata] = []
        for user in users:
            usersList.append(
                TUserMetadata(
                    userId=str(user.id),
                    avatarUrl=(
                        user.avatar.imageUrl
                        if hasattr(user, "avatar") and user.avatar
                        else None
                    ),
                )
            )

    return (200, {"usersAvatarMetadat": jsonable_encoder(usersList)})


def update_user_metadata(
    body: TUpdateMetadata, user: User
) -> tuple[int, dict[str, Any] | None]:
    logging.info(f"updating user {user.id} metadata to avatarId {body.avatarId}")
    with Session(engine) as session:
        query = select(Avatar).where(Avatar.id == body.avatarId)
        avatar = session.exec(query).first()
        if avatar:
            logging.info(f"avatar with id {body.avatarId} found")
            query = select(User).where(User.id == user.id)
            foundUser = session.exec(query).first()
            if foundUser:
                foundUser.avatarId = avatar.id
                session.add(foundUser)
                session.commit()
            else:
                raise ValueError(f"User with user id {user.id} not found")
            return 200, jsonable_encoder(f"added avatar {avatar.id} to user {user.id}")
        else:
            raise ValueError(f"no avatar found for the id {body.avatarId}")
