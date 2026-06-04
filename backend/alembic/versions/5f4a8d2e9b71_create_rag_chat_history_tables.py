"""create rag chat history tables

Revision ID: 5f4a8d2e9b71
Revises: c0bcd2a2f6e8
Create Date: 2026-06-04 15:10:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "5f4a8d2e9b71"
down_revision: str | None = "c0bcd2a2f6e8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create RAG chat session and message tables."""
    op.create_table(
        "rag_chat_sessions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rag_chat_sessions_is_deleted"), "rag_chat_sessions", ["is_deleted"])
    op.create_index(op.f("ix_rag_chat_sessions_user_id"), "rag_chat_sessions", ["user_id"])

    op.create_table(
        "rag_chat_messages",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["rag_chat_sessions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rag_chat_messages_role"), "rag_chat_messages", ["role"])
    op.create_index(op.f("ix_rag_chat_messages_session_id"), "rag_chat_messages", ["session_id"])
    op.create_index(op.f("ix_rag_chat_messages_user_id"), "rag_chat_messages", ["user_id"])


def downgrade() -> None:
    """Drop RAG chat session and message tables."""
    op.drop_index(op.f("ix_rag_chat_messages_user_id"), table_name="rag_chat_messages")
    op.drop_index(op.f("ix_rag_chat_messages_session_id"), table_name="rag_chat_messages")
    op.drop_index(op.f("ix_rag_chat_messages_role"), table_name="rag_chat_messages")
    op.drop_table("rag_chat_messages")

    op.drop_index(op.f("ix_rag_chat_sessions_user_id"), table_name="rag_chat_sessions")
    op.drop_index(op.f("ix_rag_chat_sessions_is_deleted"), table_name="rag_chat_sessions")
    op.drop_table("rag_chat_sessions")
