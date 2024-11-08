import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import JSONResponse

from middleware.user import user_middleware
from service.space import add_element_to_space, create_space, get_space
from validator_schema.space import TAddElementToSpace, TCreateSpace

logging.basicConfig(level=logging.DEBUG)

router = APIRouter(dependencies=[Depends(user_middleware)])


@router.post("/space")
async def create_avatar_route(body: TCreateSpace, request: Request):
    try:
        user = request.get("state", {}).get("user", {})
        status, data = create_space(body, user)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=str(error.args[0]), status_code=400)


@router.get("/space/{spaceId}")
async def get_space_route(
    spaceId: Annotated[str, Path(title="elementId")], request: Request
):
    try:
        status, data = get_space(spaceId)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=str(error.args[0]), status_code=400)


@router.post("/space/element")
async def add_element_to_space_route(body: TAddElementToSpace, request: Request):
    try:
        user = request.get("state", {}).get("user", {})
        status, data = add_element_to_space(body, user)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=str(error.args[0]), status_code=400)
