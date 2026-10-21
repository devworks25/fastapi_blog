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
    db_connection = get_db_connection()
    try:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 1")
            latest_post = cursor.fetchone()
    except psycopg2.Error:
        logger.exception("Failed to fetch the latest post from the database")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch the latest post from the database",
        )
    finally:
        db_connection.close()
        
    return {"data": latest_post}



def get_post(post_id: int):
    db_connection = get_db_connection()
    try:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
            post = cursor.fetchone()
    except psycopg2.Error:
        logger.exception("Failed to fetch post from the database")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch post from the database",
        )
    finally:
        db_connection.close()
        
    return {"data": post}

def delete_post(post_id: int):
    db_connection = get_db_connection()
    try:
        with db_connection.cursor() as cursor:
            cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
    except psycopg2.Error:
        logger.exception("Failed to delete post from the database")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete post from the database",
        )
    finally:
        db_connection.close()
  


def update_post(post_id: int, post_dict: dict):
    post_dict["id"] = post_id
    db_connection = get_db_connection()
    try:
        with db_connection.cursor() as cursor:
            cursor.execute("UPDATE posts SET title = %s, content = %s WHERE id = %s", (post_dict["title"], post_dict["content"], post_id))
    except psycopg2.Error:
        logger.exception("Failed to update post in the database")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update post in the database",
        )
    finally:
        db_connection.close()
        
    return {"data": post_dict}
    