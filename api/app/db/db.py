from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import  SQLModel, create_engine

engine = create_engine(
    "postgresql://username:password@localhost:5432/database", echo=True
)


def init_db():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
