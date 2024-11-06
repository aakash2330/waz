from fastapi import FastAPI
from db.db import lifespan
from router import admin, users


app = FastAPI(lifespan=lifespan)
app.include_router(users.router, prefix="/user", tags=["user"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"goodbye": "world"}
