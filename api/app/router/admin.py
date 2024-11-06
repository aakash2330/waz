from fastapi import APIRouter
from fastapi.responses import JSONResponse
from service.users import add_user_to_db
from validator_schema.users import TSignup
import logging

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


@router.post("/avatar")
async def signup(body: TSignup):
    try:
        status, data = add_user_to_db(body)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=None, status_code=400)
