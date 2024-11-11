import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from db.db import lifespan
from router import admin, users
from service.users import add_user_to_db, user_sign_in
from validator_schema.users import TSignin, TSignup
import db.schema

logging.basicConfig(level=logging.DEBUG)


app = FastAPI(lifespan=lifespan)

app.include_router(users.router, prefix="/user", tags=["user"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"goodbye": "world"}


@app.post("/signup")
async def signup(body: TSignup):
    try:
        status, data = add_user_to_db(body)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=str(error.args[0]), status_code=400)


@app.post("/signin")
async def signin(body: TSignin):
    try:
        status, data = user_sign_in(body)
        return JSONResponse(content=data, status_code=status)
    except Exception as error:
        logging.error(error)
        return JSONResponse(content=str(error.args[0]), status_code=400)
