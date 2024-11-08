import logging

from sqlmodel import Session, select

from db.db import engine
from validator_schema.avatar import TCreateAvatar
from validator_schema.element import TCreateElement, TUpdateElement
from db.schema import Avatar, Element

logging.basicConfig(level=logging.DEBUG)


def create_avatar(data: TCreateAvatar) -> tuple[int, dict[str, str] | None]:
    logging.info(f"creating avatar ${data.name}")
    with Session(engine) as session:
        avatar = Avatar(imageUrl=data.imageUrl, name=data.name)
        session.add(avatar)
        session.commit()
        session.refresh(avatar)
        session.close()
    return 200, {"avatarId": str(avatar.id)}


def create_element(data: TCreateElement) -> tuple[int, dict[str, str] | None]:

    logging.info(f"creating element ${data.imageUrl}")
    with Session(engine) as session:
        element = Element(
            imageUrl=data.imageUrl,
            height=data.height,
            width=data.width,
            static=data.static,
            name=data.name,
        )
        session.add(element)
        session.commit()
        session.refresh(element)
        session.close()
    return 200, {"id": str(element.id)}


def update_element(data: TUpdateElement) -> tuple[int, dict[str, str] | None]:

    logging.info(f"updating element ${data.id}")
    with Session(engine) as session:
        query = select(Element).where(Element.id == data.id)
        result = session.exec(query)
        element = result.one_or_none()
        if element:
            logging.info("element found to be updated")
            element.imageUrl = data.imageUrl
            session.add(element)
            session.commit()
            session.refresh(element)
            session.close()
            return 200, {"id": str(element.id)}
        else:
            logging.error("Element Not Found")
            raise ValueError("Element Not Found")
