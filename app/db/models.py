from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base, engine


class PostRecord(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("TRUE"),
    )
    author: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )
    image: Mapped[str | None] = mapped_column(String, nullable=True)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
