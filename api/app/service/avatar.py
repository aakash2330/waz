from db.schema import Avatar
import logging
from typing import Any
from sqlmodel import Session, select
from db.db import engine
from fastapi.encoders import jsonable_encoder

logging.basicConfig(level=logging.DEBUG)


def get_all_avatars() -> tuple[int, dict[str, Any] | None]:
    logging.info("fetching all available avatars")
    with Session(engine) as session:
        query = select(Avatar)
        avatars = session.exec(query).unique().all()
        if avatars:
            return 200, jsonable_encoder(avatars)
        else:
            raise ValueError("no avatars available doesn't exist")
