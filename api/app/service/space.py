import logging
from typing import Any, Sequence
from fastapi.encoders import jsonable_encoder
from db.db import engine
from sqlmodel import Session, select
from db.schema import Element, Space, SpaceElement, User
from validator_schema.element import TDeleteElement
from validator_schema.space import (
    TAddElementToSpace,
    TCheckSpaceId,
    TCreateSpace,
)

logging.basicConfig(level=logging.DEBUG)


def check_space_id_exists(data: TCheckSpaceId):
    with Session(engine) as session:
        query = select(Space).where(Space.id == data.spaceId)
        space = session.exec(query).first()
        if not space:
            logging.error(f"couldn't find space with space Id {data.spaceId}")
            return 200, False
        logging.info(f"space found with space Id {data.spaceId}")
        return 200, True


def create_space(data: TCreateSpace, user: User) -> tuple[int, dict[str, str] | None]:
    logging.info(f"creating Space ${data.name}")
    with Session(engine) as session:
        if data.spaceId:
            with Session(engine) as session:
                logging.info(f"looking for space with the spaceId {data.spaceId}")
                query = select(Space).where(Space.id == data.spaceId)
                space = session.exec(query).first()
                if space:
                    clonedSpace = Space(
                        thumbnail=space.thumbnail,
                        name=f"{data.name}",
                        width=space.width,
                        height=space.height,
                        creatorId=user.id,
                    )
                    session.add(clonedSpace)
                    # modify spaceElements from the existing space to have the new spaceId
                    for spaceElement in space.spaceElements:
                        clonedElement = SpaceElement(
                            name=f"{data.name}_{spaceElement.name}",
                            x=spaceElement.x,
                            y=spaceElement.y,
                            space_id=clonedSpace.id,
                            element_id=spaceElement.element.id,
                        )
                        session.add(clonedElement)
                        session.flush()
                    session.commit()
                    return 200, {"spaceId": str(clonedSpace.id)}
                else:
                    raise ValueError(
                        f"Couldn't find space with the space Id {data.spaceId}"
                    )
            # create a new space and copy the configuration of the given space id to the newly created space
        else:
            if data.width and data.height:
                logging.info(f"creating new space with {data}")
                space = Space(
                    name=data.name,
                    height=data.height,
                    width=data.width,
                    creatorId=user.id,
                )
                session.add(space)
                session.commit()
                session.refresh(space)
                return 200, {"spaceId": str(space.id)}
            else:
                logging.info("need both width and height to create new space")
                raise ValueError("need both width and height to create new space")


def get_space(spaceId: str) -> tuple[int, dict[str, Any] | None]:
    logging.info(f"fetching space with spaceId {spaceId}")
    with Session(engine) as session:
        space = session.exec(select(Space).where(Space.id == spaceId)).first()
        if space:
            space_dict = space.__dict__.get("spaceElements")
            print(f"space_dict --------------------------{space_dict}")
            return 200, space_dict
        else:
            raise ValueError(f"space with {spaceId} doesn't exist")


def get_user_spaces(user: User) -> tuple[int, dict[str, Any] | None]:
    logging.info(f"fetching all spaces for user {user.id}")
    with Session(engine) as session:
        query = select(Space).where(Space.creatorId == user.id)
        spaces = session.exec(query).unique().all()
        if spaces:
            return 200, jsonable_encoder(spaces)
        else:
            raise ValueError(f"space for user {user.id} doesn't exist")


def add_element_to_space(
    data: TAddElementToSpace, user: User
) -> tuple[int, dict[str, str] | None]:
    logging.info(
        f"trying to adding element with id {data.elementId} to space with id {data.spaceId}"
    )
    with Session(engine) as session:
        # fetch space
        query = select(Space).where(
            Space.id == data.spaceId, Space.creatorId == user.id
        )
        space = session.exec(query).first()
        if not space:
            logging.error(f"space with {data.spaceId} doesn't exist")
            raise ValueError(f"space with {data.spaceId} doesn't exist")

        space_elements_dict = jsonable_encoder(space.spaceElements)

        elementPresentAtXY = None
        for element in space_elements_dict:
            if element["x"] and element["y"]:
                if element["x"] == data.x and element["y"] == data.y:
                    elementPresentAtXY = element

        if elementPresentAtXY:
            logging.error(
                f"can't add element at x - {data.x} anda y - {data.y} as an element is already present on that position "
            )
            raise ValueError(
                f"can't add element at x - {data.x} anda y - {data.y} as an element is already present on that position "
            )

        # fetch element
        query = select(Element).where(Element.id == data.elementId)
        element = session.exec(query).first()

        if not element:
            logging.error(f"element with {data.elementId} doesn't exis")
            raise ValueError(f"element with {data.elementId} doesn't exis")

        # create new space element
        spaceElement = SpaceElement(
            name=data.name, x=data.x, y=data.y, space_id=space.id, element_id=element.id
        )
        session.add(spaceElement)
        session.commit()
        session.refresh(spaceElement)
        session.close()
        return 200, {"spaceElemetId": str(spaceElement.id)}


def delete_space_element(
    data: TDeleteElement, user: User
) -> tuple[int, dict[str, str] | None]:
    logging.info(f"deleting space element with element id {data.id}")
    # find spaceElement with the given userId , if owns delete it
    with Session(engine) as session:
        # fetch space
        query = select(SpaceElement).where(SpaceElement.id == data.id)
        spaceElement = session.exec(query).first()
        if not spaceElement:
            raise ValueError(f"Couldn't find spaceElement with theId {data.id}")
        if spaceElement.space:
            if spaceElement.space.creatorId == user.id:
                session.delete(spaceElement)
                session.commit()
                session.close()
                return 200, {"spaceElementDeleted": str(spaceElement.id)}
            else:
                raise ValueError(
                    f"User {user.username} doesn't own the spaceElement with id {data.id}"
                )
        raise ValueError(f"Unable to delete spaceElement with id  {data.id}")


def get_all_elements() -> tuple[int, dict[str, Sequence[Element]]]:
    with Session(engine) as session:
        logging.info("fetching all elements")
        # fetch space
        query = select(Element)
        elements = session.exec(query).unique().all()
        if not elements:
            raise ValueError("unable to get all elements")

    return 200, {"elements": jsonable_encoder(elements)}
