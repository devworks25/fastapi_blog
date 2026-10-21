from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    image: Optional[str] = None
