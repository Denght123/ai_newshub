from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.categories import Category
    from models.news import News
    from models.users import User


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    news_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("news.id"),
        index=True,
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    angle: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_reader: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("categories.id"),
        index=True,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True, nullable=False)
    value_score: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    difficulty_score: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    traffic_score: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, index=True, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
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

    news: Mapped["News | None"] = relationship(back_populates="topics")
    category: Mapped["Category | None"] = relationship(back_populates="topics")
    creator: Mapped["User"] = relationship(back_populates="topics")
