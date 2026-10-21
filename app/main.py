
from fastapi import FastAPI

from .routers.posts import router

app = FastAPI()
app.include_router(router)
