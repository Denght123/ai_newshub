from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.daily_digest_runs import DailyDigestRun
    from models.rag_chunks import RagChunk
    from models.users import User


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(LONGTEXT, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(800), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, index=True, nullable=True)
    digest_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    credibility: Mapped[str] = mapped_column(String(30), default="unknown", index=True, nullable=False)
    run_id: Mapped[str | None] = mapped_column(
        String(80),
        ForeignKey("daily_digest_runs.run_id"),
        index=True,
        nullable=True,
    )
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
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )

    # RAG 问答主要检索 chunks，再回到 document 拿标题、日期和来源。
    chunks: Mapped[list["RagChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
    digest_run: Mapped["DailyDigestRun | None"] = relationship(back_populates="documents")
    creator: Mapped["User"] = relationship()
