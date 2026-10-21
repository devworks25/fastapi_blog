import logging
from random import randrange

import psycopg2
from fastapi import HTTPException, Response, status

from ..db.database import get_db_connection
from ..helper.helpers import find_post, my_posts

logger = logging.getLogger(__name__)


def root():
    return {"message": "Hello World"}


def get_posts():
    db_connection = get_db_connection()
    try:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM posts")
            posts = cursor.fetchall()
    except psycopg2.Error:
        logger.exception("Failed to fetch posts from the database")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch posts from the database",
        )
    return {"data": posts}


def create_post(post_dict: dict):
    db_connection = get_db_connection()
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *",
                (post_dict["title"], post_dict["content"], post_dict["published"]),
            )
            new_post = cursor.fetchone()
        db_connection.commit()
        return {"data": new_post}
    except psycopg2.Error:
        db_connection.rollback()
        logger.exception("Failed to create a new post in the database")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create a new post in the database",
        )
    finally:
        db_connection.close()


def get_latest_post():
    if not my_posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts found",
        )
    return {"latest_post": my_posts[-1]}


def get_post(post_id: int):
    post = find_post(post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post not found for the id: {post_id}",
        )
    return {"post_detail": post}


def delete_post(post_id: int):
    post = find_post(post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post not found for the id: {post_id}",
        )
    my_posts.remove(post)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def update_post(post_id: int, post_dict: dict):
    post_dict["id"] = post_id
    for index, existing_post in enumerate(my_posts):
        if existing_post["id"] == post_id:
            my_posts[index] = post_dict
            return {"data": post_dict}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post not found for the id: {post_id}",
    )