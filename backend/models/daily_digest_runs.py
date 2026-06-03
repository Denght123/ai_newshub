from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.knowledge_documents import KnowledgeDocument
    from models.users import User


class DailyDigestRun(Base):
    __tablename__ = "daily_digest_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    digest_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="reserved", index=True, nullable=False)
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    collected_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    document_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_sources: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )

    # 一个采集任务可以沉淀多条知识文档。
    documents: Mapped[list["KnowledgeDocument"]] = relationship(back_populates="digest_run")
    creator: Mapped["User"] = relationship()
