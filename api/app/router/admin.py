import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse

from middleware.admin import admin_middleware
from service.admin import create_avatar, create_element, update_element
from validator_schema.avatar import TCreateAvatar
from validator_schema.element import TCreateElement, TUpdateElement, TUpdateElementBody

logging.basicConfig(level=logging.DEBUG)

router = APIRouter(dependencies=[Depends(admin_middleware)])


@router.post("/avatar")
async def create_avatar_route(body: TCreateAvatar):
    try:
        status, data = create_avatar(body)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=None, status_code=400)


@router.post("/element")
async def create_element_route(body: TCreateElement):
    try:
        status, data = create_element(body)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=None, status_code=400)


@router.put("/element/{elementId}")
async def update_element_route(
    elementId: Annotated[str, Path(title="elementId")],
    body: TUpdateElementBody,
):
    try:
        status, data = update_element(
            TUpdateElement(id=elementId, imageUrl=body.imageUrl)
        )
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=None, status_code=400)
