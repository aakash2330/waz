import logging

import jwt
from fastapi import HTTPException, Request, status
from sqlmodel import Session, select

from db.db import engine
from db.schema import User
from validator_schema.users import TRole

logging.basicConfig(level=logging.DEBUG)


def user_middleware(request: Request):
    try:
        logging.info(f"Running user_middleware for path: {request.url.path}")
        auth_header = dict(request.scope["headers"]).get(b"authorization")
        if auth_header is None:
            raise ValueError("Couldn't find Auth Header")
        token = auth_header.split()[1]

        logging.info("decoding jwt token")
        payload = jwt.decode(token.decode(), "secret", algorithms=["HS256"])

        if payload.get("type") == TRole.user or payload.get("type") == TRole.admin:
            logging.info(f"user has the role {payload.get("type")}")
            with Session(engine) as session:
                query = select(User).where(User.username == payload.get("username"))
                user = session.exec(query).first()
                request.state.user = user
                return request

        raise ValueError("Doesn't have correct role 'user'")
    except Exception as error:
        logging.error(error)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
