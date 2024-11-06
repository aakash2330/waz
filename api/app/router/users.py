from fastapi import APIRouter
from fastapi.responses import JSONResponse
from service.users import add_user_to_db, user_sign_in
from validator_schema.users import TSignin, TSignup
import logging

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


@router.post("/signup")
async def signup(body: TSignup):
    try:
        status, data = add_user_to_db(body)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=None, status_code=400)


@router.post("/signin")
async def signin(body: TSignin):
    try:
        status, data = user_sign_in(body)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=None, status_code=403)
