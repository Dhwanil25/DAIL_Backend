"""Initial schema matching Caspio DAIL tables exactly.

Four tables: cases, dockets, documents, secondary_sources.
All columns match Caspio field names in snake_case.
FK relationships use case_number -> cases.record_number (matches Caspio join key).

Revision ID: 001
Revises: -
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Cases table (Caspio: Case_Table, 33 active columns) ──────────
    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("record_number", sa.Integer(), unique=True, nullable=False),
        sa.Column("case_slug", sa.Text()),
        sa.Column("caption", sa.Text(), nullable=False),
        sa.Column("brief_description", sa.Text()),
        # Area / Application
        sa.Column("area_of_application", sa.Text()),
        sa.Column("area_of_application_text", sa.Text()),
        # Issues
        sa.Column("issue_text", sa.Text()),
        sa.Column("issue_list", sa.Text()),
        # Cause of Action
        sa.Column("cause_of_action_list", sa.Text()),
        sa.Column("cause_of_action_text", sa.Text()),
        # Algorithm
        sa.Column("name_of_algorithm_list", sa.Text()),
        sa.Column("name_of_algorithm_text", sa.Text()),
        # Class Action
        sa.Column("class_action_list", sa.Text()),
        sa.Column("class_action", sa.Text()),
        # Organizations
        sa.Column("organizations_involved", sa.Text()),
        # Jurisdiction
        sa.Column("jurisdiction_filed", sa.Text()),
        sa.Column("date_action_filed", sa.Date()),
        sa.Column("current_jurisdiction", sa.Text()),
        sa.Column("jurisdiction_type", sa.Text()),
        sa.Column("jurisdiction_type_text", sa.Text()),
        sa.Column("jurisdiction_name", sa.Text()),
        # Opinions
        sa.Column("published_opinions", sa.Text()),
        sa.Column("published_opinions_binary", sa.Boolean(), server_default="false"),
        # Status
        sa.Column("status_disposition", sa.Text()),
        # Timestamps
        sa.Column("date_added", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("last_update", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        # Notes
        sa.Column("progress_notes", sa.Text()),
        sa.Column("researcher", sa.Text()),
        # Summaries
        sa.Column("summary_of_significance", sa.Text()),
        sa.Column("summary_facts_activity", sa.Text()),
        # Recent activity
        sa.Column("most_recent_activity", sa.Text()),
        sa.Column("most_recent_activity_date", sa.Date()),
        # Search
        sa.Column("keyword", sa.Text()),
        sa.Column("search_vector", TSVECTOR),
    )

    # Indexes
    op.create_index("ix_cases_record_number", "cases", ["record_number"])
    op.create_index("ix_cases_status", "cases", ["status_disposition"])
    op.create_index("ix_cases_jurisdiction_type", "cases", ["jurisdiction_type"])
    op.create_index("ix_cases_area", "cases", ["area_of_application"])
    op.create_index("ix_cases_date_filed", "cases", ["date_action_filed"])
    op.create_index(
        "ix_cases_search_vector", "cases", ["search_vector"],
        postgresql_using="gin",
    )

    # Full-text search trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION update_case_search_vector()
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', coalesce(NEW.caption, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(NEW.brief_description, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(NEW.keyword, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(NEW.issue_text, '')), 'C') ||
                setweight(to_tsvector('english', coalesce(NEW.cause_of_action_text, '')), 'C') ||
                setweight(to_tsvector('english', coalesce(NEW.organizations_involved, '')), 'C') ||
                setweight(to_tsvector('english', coalesce(NEW.summary_of_significance, '')), 'D') ||
                setweight(to_tsvector('english', coalesce(NEW.summary_facts_activity, '')), 'D');
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trig_cases_search_vector
        BEFORE INSERT OR UPDATE ON cases
        FOR EACH ROW EXECUTE FUNCTION update_case_search_vector();
    """)

    # ── Dockets table (Caspio: Docket_Table) ─────────────────────────
    op.create_table(
        "dockets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "case_number", sa.Integer(),
            sa.ForeignKey("cases.record_number", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("court", sa.Text()),
        sa.Column("number", sa.Text()),
        sa.Column("link", sa.Text()),
    )
    op.create_index("ix_dockets_case_number", "dockets", ["case_number"])

    # ── Documents table (Caspio: Document_Table) ─────────────────────
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "case_number", sa.Integer(),
            sa.ForeignKey("cases.record_number", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("court", sa.Text()),
        sa.Column("date", sa.Date()),
        sa.Column("link", sa.Text()),
        sa.Column("cite_or_reference", sa.Text()),
    )
    op.create_index("ix_documents_case_number", "documents", ["case_number"])

    # ── Secondary Sources table (Caspio: Secondary_Source_Coverage) ──
    op.create_table(
        "secondary_sources",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "case_number", sa.Integer(),
            sa.ForeignKey("cases.record_number", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("secondary_source_link", sa.Text()),
        sa.Column("secondary_source_title", sa.Text()),
    )
    op.create_index("ix_secondary_sources_case_number", "secondary_sources", ["case_number"])


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trig_cases_search_vector ON cases;")
    op.execute("DROP FUNCTION IF EXISTS update_case_search_vector();")
    op.drop_table("secondary_sources")
    op.drop_table("documents")
    op.drop_table("dockets")
    op.drop_table("cases")
