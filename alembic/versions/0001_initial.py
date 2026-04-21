"""Initial migration — create documents, flashcards, reviews tables.

Revision ID: 0001
Revises: 
Create Date: 2026-04-04
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("raw_text", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="uploaded"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "flashcards",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "document_id",
            sa.String(36),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("ease_factor", sa.Float, nullable=False, server_default="2.5"),
        sa.Column("interval", sa.Integer, nullable=False, server_default="1"),
        sa.Column("repetitions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("due_date", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "flashcard_id",
            sa.String(36),
            sa.ForeignKey("flashcards.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("quality", sa.Integer, nullable=False),
        sa.Column("scheduled_days", sa.Integer, nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("flashcards")
    op.drop_table("documents")
