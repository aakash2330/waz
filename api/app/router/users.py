import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import JSONResponse

from middleware.user import user_middleware
from service.avatar import get_all_avatars
from service.space import (
    add_element_to_space,
    check_space_id_exists,
    create_space,
    delete_space_element,
    get_all_elements,
    get_space,
    get_user_spaces,
)
from service.users import get_bulk_user_metadata, update_user_metadata
from validator_schema.avatar import TUpdateMetadata
from validator_schema.element import TDeleteElement
from validator_schema.space import TAddElementToSpace, TCheckSpaceId, TCreateSpace
from validator_schema.users import TGetUserMetadata

logging.basicConfig(level=logging.DEBUG)

router = APIRouter(dependencies=[Depends(user_middleware)])


@router.post("/metadata")
async def update_user_metadata_route(body: TUpdateMetadata, request: Request):
    try:
        user = request.get("state", {}).get("user", {})
        status, data = update_user_metadata(body, user)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=str(error.args[0]), status_code=400)


@router.get("/metadata/bulk")
async def get_bulk_user_metadata_route(ids: str | None = None):
    if not ids:
        raise ValueError("no ids found in query params")
    idsArr = ids.split(",")
    try:
        status, data = get_bulk_user_metadata(TGetUserMetadata(ids=idsArr))
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=str(error.args[0]), status_code=400)


@router.get("/avatar/all")
async def get_all_avatars_route():
    try:
        status, data = get_all_avatars()
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=str(error.args[0]), status_code=400)


@router.post("/space")
async def create_space_route(body: TCreateSpace, request: Request):
    try:
        user = request.get("state", {}).get("user", {})
        status, data = create_space(body, user)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=str(error.args[0]), status_code=400)


@router.get("/spaces/all")
async def get_user_spaces_route(request: Request):
    try:
        user = request.get("state", {}).get("user", {})
        status, data = get_user_spaces(user)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=str(error.args[0]), status_code=400)


@router.get("/elements")
async def get_all_elements_route():
    try:
        status, data = get_all_elements()
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


@router.delete("/space/element")
async def delete_space_element_route(body: TDeleteElement, request: Request):
    try:
        user = request.get("state", {}).get("user", {})
        status, data = delete_space_element(body, user)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=str(error.args[0]), status_code=400)


@router.get("/space/check/{spaceId}")
async def check_space_id_exists_route(
    spaceId: Annotated[str, Path(title="elementId")], request: Request
):
    try:
        status, data = check_space_id_exists(TCheckSpaceId(spaceId=spaceId))
        return JSONResponse(content={"space_exists": data}, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=str(error.args[0]), status_code=400)
