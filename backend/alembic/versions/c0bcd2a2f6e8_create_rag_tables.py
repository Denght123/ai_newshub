"""create rag tables

Revision ID: c0bcd2a2f6e8
Revises: bb1237c89332
Create Date: 2026-06-03 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = "c0bcd2a2f6e8"
down_revision: Union[str, Sequence[str], None] = "bb1237c89332"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create RAG knowledge-base tables."""
    op.create_table(
        "daily_digest_runs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.String(length=80), nullable=False),
        sa.Column("digest_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=True),
        sa.Column("collected_count", sa.Integer(), nullable=False),
        sa.Column("document_count", sa.Integer(), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.Column("failed_sources", sa.JSON(), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_daily_digest_runs_created_by"), "daily_digest_runs", ["created_by"])
    op.create_index(op.f("ix_daily_digest_runs_digest_date"), "daily_digest_runs", ["digest_date"])
    op.create_index(op.f("ix_daily_digest_runs_run_id"), "daily_digest_runs", ["run_id"], unique=True)
    op.create_index(op.f("ix_daily_digest_runs_status"), "daily_digest_runs", ["status"])

    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("content", mysql.LONGTEXT(), nullable=True),
        sa.Column("source_name", sa.String(length=120), nullable=True),
        sa.Column("source_url", sa.String(length=800), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("digest_date", sa.Date(), nullable=False),
        sa.Column("credibility", sa.String(length=30), nullable=False),
        sa.Column("run_id", sa.String(length=80), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["run_id"], ["daily_digest_runs.run_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_knowledge_documents_created_by"), "knowledge_documents", ["created_by"])
    op.create_index(op.f("ix_knowledge_documents_credibility"), "knowledge_documents", ["credibility"])
    op.create_index(op.f("ix_knowledge_documents_digest_date"), "knowledge_documents", ["digest_date"])
    op.create_index(op.f("ix_knowledge_documents_is_deleted"), "knowledge_documents", ["is_deleted"])
    op.create_index(op.f("ix_knowledge_documents_published_at"), "knowledge_documents", ["published_at"])
    op.create_index(op.f("ix_knowledge_documents_run_id"), "knowledge_documents", ["run_id"])

    op.create_table(
        "rag_chunks",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("document_id", sa.BigInteger(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("digest_date", sa.Date(), nullable=False),
        sa.Column("source_url", sa.String(length=800), nullable=True),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("embedding_model", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["knowledge_documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rag_chunks_chunk_index"), "rag_chunks", ["chunk_index"])
    op.create_index(op.f("ix_rag_chunks_digest_date"), "rag_chunks", ["digest_date"])
    op.create_index(op.f("ix_rag_chunks_document_id"), "rag_chunks", ["document_id"])


def downgrade() -> None:
    """Drop RAG knowledge-base tables."""
    op.drop_index(op.f("ix_rag_chunks_document_id"), table_name="rag_chunks")
    op.drop_index(op.f("ix_rag_chunks_digest_date"), table_name="rag_chunks")
    op.drop_index(op.f("ix_rag_chunks_chunk_index"), table_name="rag_chunks")
    op.drop_table("rag_chunks")

    op.drop_index(op.f("ix_knowledge_documents_run_id"), table_name="knowledge_documents")
    op.drop_index(op.f("ix_knowledge_documents_published_at"), table_name="knowledge_documents")
    op.drop_index(op.f("ix_knowledge_documents_is_deleted"), table_name="knowledge_documents")
    op.drop_index(op.f("ix_knowledge_documents_digest_date"), table_name="knowledge_documents")
    op.drop_index(op.f("ix_knowledge_documents_credibility"), table_name="knowledge_documents")
    op.drop_index(op.f("ix_knowledge_documents_created_by"), table_name="knowledge_documents")
    op.drop_table("knowledge_documents")

    op.drop_index(op.f("ix_daily_digest_runs_status"), table_name="daily_digest_runs")
    op.drop_index(op.f("ix_daily_digest_runs_run_id"), table_name="daily_digest_runs")
    op.drop_index(op.f("ix_daily_digest_runs_digest_date"), table_name="daily_digest_runs")
    op.drop_index(op.f("ix_daily_digest_runs_created_by"), table_name="daily_digest_runs")
    op.drop_table("daily_digest_runs")
