
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db.models import create_tables
from .routers.posts import router


@asynccontextmanager
async def lifespan(app: FastAPI):
	create_tables()
	yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
