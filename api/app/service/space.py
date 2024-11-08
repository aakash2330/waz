import logging
from typing import Any
import jsonpickle
from fastapi.encoders import jsonable_encoder
from db.db import engine
from sqlmodel import Session, select
from db.schema import Element, Space, SpaceElement, User
from validator_schema.space import TAddElementToSpace, TCreateSpace

logging.basicConfig(level=logging.DEBUG)


def create_space(data: TCreateSpace, user: User) -> tuple[int, dict[str, str] | None]:
    logging.info(f"creating Space ${data.name}")
    with Session(engine) as session:
        if data.spaceId:
            with Session(engine) as session:
                logging.info(f"looking for space with the spaceId {data.spaceId}")
                query = select(Space).where(Space.id == data.spaceId)
                space = session.exec(query).first()
                if space:
                    print(f"here is the space - {space}")
                    return 200, {"spaceId": str(space.id)}
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
                print(f"created space {space}")
                session.add(space)
                session.commit()
                session.refresh(space)
                session.close()
                return 200, {"spaceId": str(space.id)}
            else:
                logging.info("need both width and height to create new space")
                raise ValueError("need both width and height to create new space")
            # create new empty space with the given dimentions


def get_space(spaceId: str) -> tuple[int, dict[str, Any] | None]:
    logging.info(f"fetching space with spaceId {spaceId}")
    with Session(engine) as session:
        space = session.exec(select(Space)).first()
        if space:
            jsonifiedSpace = jsonpickle.encode(space)
            print(f"space--------------------{jsonifiedSpace}")
            return 200, jsonable_encoder(space)
        else:
            raise ValueError(f"space with {spaceId} doesn't exist")


def add_element_to_space(
    data: TAddElementToSpace, user: User
) -> tuple[int, dict[str, str] | None]:
    logging.info(
        f"adding element with id {data.elementId} to space with id {data.spaceId}"
    )
    with Session(engine) as session:
        # fetch space
        query = select(Space).where(Space.id == data.spaceId)
        space = session.exec(query).first()
        print(f"space---------------{space}")
        if not space:
            logging.error(f"space with {data.spaceId} doesn't exist")
            raise ValueError(f"space with {data.spaceId} doesn't exist")

        #        elementPresentAtXY = (
        #            element
        #            for element in space.spaceElements
        #            if element.x == data.x and element.y == data.y
        #        )
        #        print(f"elementATXY {elementPresentAtXY}")
        #        if elementPresentAtXY:
        #            logging.error(
        #                f"can't add element at x - {data.x} anda y - {data.y} as an element is already present on that position "
        #            )
        #            raise ValueError(
        #                f"can't add element at x - {data.x} anda y - {data.y} as an element is already present on that position "
        #            )

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
