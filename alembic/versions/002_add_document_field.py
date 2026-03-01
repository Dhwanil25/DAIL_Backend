"""Add 'document' column to documents table.

The Caspio Document_Table export includes a 'document' field
(document title/description) that was missing from the initial schema.

Revision ID: 002
Revises: 001
"""

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("document", sa.Text()))


def downgrade() -> None:
    op.drop_column("documents", "document")
