from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    image: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostData(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    #image: Optional[str] = None


class PostResponse(BaseModel):
    data: PostData


class PostListResponse(BaseModel):
    data: list[PostData]

