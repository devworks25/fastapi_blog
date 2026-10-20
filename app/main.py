from typing import Optional

from fastapi import Body, FastAPI,Response,status,HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, {"title": "favorite foods", "content": "I like pizza", "id": 2}]


def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Get all posts
@app.get("/posts",status_code=status.HTTP_200_OK)
async def get_posts():
    return {"data": my_posts}

# Create a post
@app.post("/posts",status_code=status.HTTP_201_CREATED)
async def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

# Get the latest post
@app.get("/posts/latest",status_code=status.HTTP_200_OK)
async def get_latest_post():
    post = my_posts[len(my_posts) - 1]
    return {"latest_post": post}

# Get a specific post by id
@app.get("/posts/{id}",status_code=status.HTTP_200_OK)
async def get_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post not found for the id: {id}"
            )
    return {"post_detail": post}

# Delete a specific post by id
@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post not found for the id: {id}"
            )
    my_posts.remove(post)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update a specific post by id
@app.put("/posts/{id}",status_code=status.HTTP_200_OK)
async def update_post(id: int, post: Post):
    post_dict = post.dict()
    post_dict['id'] = id
    for index, p in enumerate(my_posts):
        if p['id'] == id:
            my_posts[index] = post_dict
            return {"data": post_dict}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Post not found for the id: {id}"
        )