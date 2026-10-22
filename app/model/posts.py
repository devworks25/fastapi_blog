from sqlalchemy import select,inspect
from sqlalchemy.exc import SQLAlchemyError
from fastapi import status

from ..db.database import managed_db_session
from ..helper.exceptions import raise_database_exception, raise_http_exception
from ..db.models import PostRecord


def _post_to_dict(post: PostRecord) -> dict:
    return {
        column.name: getattr(post, column.name)
        for column in PostRecord.__table__.columns
    }


def root():
    try:
        with managed_db_session() as session:
            inspector = inspect(session.get_bind())

            if not inspector.has_table("posts"):
                raise_http_exception(
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    "Required database table 'posts' is missing",
                )

            session.execute(select(1))

    except SQLAlchemyError:
        raise_http_exception(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "App health check failed",
        )

    return {
        "status": "healthy",
        "message": "App is healthy",
    }


def get_posts():
    try:
        with managed_db_session() as session:
            posts = session.scalars(select(PostRecord)).all()
        if not posts:
            raise_http_exception(status.HTTP_404_NOT_FOUND, "No posts found")
    except SQLAlchemyError:
        raise_database_exception("Failed to fetch posts from the database")
    return {"data": [_post_to_dict(post) for post in posts]}


def create_post(post_dict: dict):
    try:
        with managed_db_session() as session:
            post = PostRecord(**post_dict)
            session.add(post)
            session.commit()
            session.refresh(post)
            return {"data": _post_to_dict(post)}
    except SQLAlchemyError:
        raise_database_exception("Failed to create a new post in the database")


def get_latest_post():
    try:
        with managed_db_session() as session:
            latest_post = session.scalar(
                select(PostRecord).order_by(PostRecord.created_at.desc()).limit(1)
            )
        if latest_post is None:
            raise_http_exception(status.HTTP_404_NOT_FOUND, "No posts found")
    except SQLAlchemyError:
        raise_database_exception("Failed to fetch the latest post from the database")
    return {"data": _post_to_dict(latest_post)}



def get_post(post_id: int):
    try:
        with managed_db_session() as session:
            post = session.get(PostRecord, post_id)
        if post is None:
            raise_http_exception(
                status.HTTP_404_NOT_FOUND,
                f"Post with id {post_id} not found",
            )
    except SQLAlchemyError:
        raise_database_exception("Failed to fetch post from the database")
    return {"data": _post_to_dict(post)}

def delete_post(post_id: int):
    try:
        with managed_db_session() as session:
            post = session.get(PostRecord, post_id)
            if post is None:
                raise_http_exception(
                    status.HTTP_404_NOT_FOUND,
                    f"Post with id {post_id} not found",
                )
            session.delete(post)
            session.commit()
    except SQLAlchemyError:
        raise_database_exception("Failed to delete post from the database")


def update_post(post_id: int, post_dict: dict):
    updated_post = {**post_dict, "id": post_id}
    try:
        with managed_db_session() as session:
            post = session.get(PostRecord, post_id)
            if post is None:
                raise_http_exception(
                    status.HTTP_404_NOT_FOUND,
                    f"Post with id {post_id} not found",
                )
            post.title = updated_post["title"]
            post.content = updated_post["content"]
            session.commit()
    except SQLAlchemyError:
        raise_database_exception("Failed to update post in the database")
    return {"data": updated_post}
