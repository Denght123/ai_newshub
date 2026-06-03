from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.knowledge_documents import KnowledgeDocument


class RagChunk(Base):
    __tablename__ = "rag_chunks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("knowledge_documents.id"),
        index=True,
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    digest_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(800), nullable=True)
    embedding: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    # 每个 chunk 属于一篇知识文档。
    document: Mapped["KnowledgeDocument"] = relationship(back_populates="chunks")
