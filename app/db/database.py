import logging
import os

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            database=os.getenv("DB_NAME", "fastapi_blog"),
            user=os.getenv("DB_USER", "fastapi_user"),
            password=os.environ["DB_PASSWORD"],
            port=int(os.getenv("DB_PORT", "5432")),
            connect_timeout=5,
            cursor_factory=RealDictCursor,
        )
        logger.info("Database connection successful")
        return conn
    except (psycopg2.Error, KeyError, ValueError):
        logger.exception("Database connection failed")
        raise