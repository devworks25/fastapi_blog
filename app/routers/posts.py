from typing import Optional

from fastapi import APIRouter, status
from pydantic import BaseModel

from ..model import posts as post_logic

router = APIRouter()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


@router.get("/")
async def root():
    return post_logic.root()


@router.get("/posts", status_code=status.HTTP_200_OK)
async def get_posts():
    return post_logic.get_posts()


@router.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    return post_logic.create_post(post.dict())


@router.get("/posts/latest", status_code=status.HTTP_200_OK)
async def get_latest_post():
    return post_logic.get_latest_post()


@router.get("/posts/{id}", status_code=status.HTTP_200_OK)
async def get_post(id: int):
    return post_logic.get_post(id)


@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    return post_logic.delete_post(id)


@router.put("/posts/{id}", status_code=status.HTTP_200_OK)
async def update_post(id: int, post: Post):
    return post_logic.update_post(id, post.dict())