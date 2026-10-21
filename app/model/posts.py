import psycopg2
from fastapi import status

from ..db.database import managed_db_connection
from ..helper.exceptions import raise_database_exception, raise_http_exception


def root():
    return {"message": "Hello World"}


def get_posts():
    try:
        with managed_db_connection() as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute("SELECT * FROM posts")
                posts = cursor.fetchall()
        if not posts:
            raise_http_exception(status.HTTP_404_NOT_FOUND, "No posts found")
    except psycopg2.Error:
        raise_database_exception("Failed to fetch posts from the database")
    return {"data": posts}


def create_post(post_dict: dict):
    try:
        with managed_db_connection() as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *",
                    (post_dict["title"], post_dict["content"], post_dict["published"]),
                )
                new_post = cursor.fetchone()
            db_connection.commit()
        return {"data": new_post}
    except psycopg2.Error:
        raise_database_exception("Failed to create a new post in the database")


def get_latest_post():
    try:
        with managed_db_connection() as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 1")
                latest_post = cursor.fetchone()
        if latest_post is None:
            raise_http_exception(status.HTTP_404_NOT_FOUND, "No posts found")
    except psycopg2.Error:
        raise_database_exception("Failed to fetch the latest post from the database")
    return {"data": latest_post}



def get_post(post_id: int):
    try:
        with managed_db_connection() as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
                post = cursor.fetchone()
        if post is None:
            raise_http_exception(
                status.HTTP_404_NOT_FOUND,
                f"Post with id {post_id} not found",
            )
    except psycopg2.Error:
        raise_database_exception("Failed to fetch post from the database")
    return {"data": post}

def delete_post(post_id: int):
    try:
        with managed_db_connection() as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
                if cursor.rowcount == 0:
                    raise_http_exception(
                        status.HTTP_404_NOT_FOUND,
                        f"Post with id {post_id} not found",
                    )
            db_connection.commit()
    except psycopg2.Error:
        raise_database_exception("Failed to delete post from the database")


def update_post(post_id: int, post_dict: dict):
    updated_post = {**post_dict, "id": post_id}
    try:
        with managed_db_connection() as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE posts SET title = %s, content = %s WHERE id = %s",
                    (updated_post["title"], updated_post["content"], post_id),
                )
                if cursor.rowcount == 0:
                    raise_http_exception(
                        status.HTTP_404_NOT_FOUND,
                        f"Post with id {post_id} not found",
                    )
            db_connection.commit()
    except psycopg2.Error:
        raise_database_exception("Failed to update post in the database")
    return {"data": updated_post}
