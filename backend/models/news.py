from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.categories import Category
    from models.tags import Tag
    from models.topics import Topic
    from models.users import User


news_tags = Table(
    "news_tags",
    Base.metadata,
    Column("news_id", BigInteger, ForeignKey("news.id"), primary_key=True),
    Column("tag_id", BigInteger, ForeignKey("tags.id"), primary_key=True),
)


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    source_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("categories.id"),
        index=True,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(30), default="unread", index=True, nullable=False)
    importance_score: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    heat_score: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    publish_time: Mapped[datetime | None] = mapped_column(DateTime, index=True, nullable=True)
    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        index=True,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )

    category: Mapped["Category | None"] = relationship(back_populates="news_items")
    creator: Mapped["User"] = relationship(back_populates="news_items")
    tags: Mapped[list["Tag"]] = relationship(
        secondary=news_tags,
        back_populates="news_items",
    )
    topics: Mapped[list["Topic"]] = relationship(back_populates="news")
