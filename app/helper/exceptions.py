import logging
from typing import NoReturn

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def raise_http_exception(status_code: int, detail: str) -> NoReturn:
    raise HTTPException(status_code=status_code, detail=detail)


def raise_database_exception(message: str) -> NoReturn:
    logger.exception("Database operation failed: %s", message)
    raise_http_exception(status.HTTP_500_INTERNAL_SERVER_ERROR, message)
