from sqlmodel import Session
from db.db import engine
from models.users import User
from validator_schema.users import TSignin, TSignup, TRole
from sqlmodel import select
import bcrypt
import jwt
from typing import Any
import logging

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
            type=TRole.user,
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
    payload: dict[str, Any] = data.model_dump(exclude={"password", "id"})
    token = jwt.encode(payload, "secret", algorithm="HS256")
    return str(token)


def user_sign_in(data: TSignin) -> tuple[int, str | None]:
    logging.info(
        f"getting user data for username -  {data.username} and comparing password"
    )
    user = find_user_by_id(data)

    logging.info("generating token for the user")

    token = generate_jwt_token(user)
    return 200, token
