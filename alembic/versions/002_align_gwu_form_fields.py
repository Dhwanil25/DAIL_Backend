"""Align cases table with GWU DAIL form fields.

Adds missing fields: issue_list, area_of_application_list, algorithm_list,
jurisdiction_filed, current_jurisdiction, researcher, published_opinions,
summary_of_significance, most_recent_activity, most_recent_activity_date.

Renames: notes → progress_notes, facts → summary_of_facts.
Changes: is_class_action (bool) → class_action (varchar).

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
    # ── Add missing columns from the GWU form ────────────────────────
    op.add_column("cases", sa.Column("issue_list", sa.String(255), comment="Standardised issue dropdown value"))
    op.add_column("cases", sa.Column("area_of_application_list", sa.String(255), comment="Standardised area dropdown value"))
    op.add_column("cases", sa.Column("algorithm_list", sa.String(500), comment="Standardised algorithm dropdown value"))
    op.add_column("cases", sa.Column("jurisdiction_filed", sa.String(255), comment="Original filing jurisdiction"))
    op.add_column("cases", sa.Column("current_jurisdiction", sa.String(255), comment="Where case currently resides"))
    op.add_column("cases", sa.Column("researcher", sa.String(255), comment="Researcher tracking this case"))
    op.add_column("cases", sa.Column("published_opinions", sa.Boolean(), server_default="false", comment="Has published opinions?"))
    op.add_column("cases", sa.Column("summary_of_significance", sa.Text(), comment="Summary of case significance"))
    op.add_column("cases", sa.Column("most_recent_activity", sa.Text(), comment="Description of most recent activity"))
    op.add_column("cases", sa.Column("most_recent_activity_date", sa.Date(), comment="Date of most recent activity"))

    # ── Rename columns to match form labels ──────────────────────────
    op.alter_column("cases", "notes", new_column_name="progress_notes")
    op.alter_column("cases", "facts", new_column_name="summary_of_facts")

    # ── Recreate search trigger with renamed column ──────────────────
    op.execute("DROP TRIGGER IF EXISTS trig_cases_search_vector ON cases;")
    op.execute("DROP FUNCTION IF EXISTS update_case_search_vector();")
    op.execute("""
        CREATE OR REPLACE FUNCTION update_case_search_vector()
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', coalesce(NEW.caption, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(NEW.brief_description, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(NEW.keywords, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(NEW.algorithm_name, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(NEW.issue_text, '')), 'C') ||
                setweight(to_tsvector('english', coalesce(NEW.cause_of_action, '')), 'C') ||
                setweight(to_tsvector('english', coalesce(NEW.organizations_involved, '')), 'C') ||
                setweight(to_tsvector('english', coalesce(NEW.summary_of_facts, '')), 'D') ||
                setweight(to_tsvector('english', coalesce(NEW.summary_of_significance, '')), 'D');
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trig_cases_search_vector
        BEFORE INSERT OR UPDATE ON cases
        FOR EACH ROW EXECUTE FUNCTION update_case_search_vector();
    """)

    # ── Convert is_class_action bool → class_action varchar ──────────
    op.add_column("cases", sa.Column("class_action", sa.String(50), comment="Class action status: Yes/No/Putative etc."))
    op.execute("UPDATE cases SET class_action = CASE WHEN is_class_action THEN 'Yes' ELSE 'No' END")
    op.drop_column("cases", "is_class_action")


def downgrade() -> None:
    # Reverse: class_action → is_class_action
    op.add_column("cases", sa.Column("is_class_action", sa.Boolean(), server_default="false"))
    op.execute("UPDATE cases SET is_class_action = CASE WHEN class_action = 'Yes' THEN true ELSE false END")
    op.drop_column("cases", "class_action")

    # Reverse renames
    op.alter_column("cases", "progress_notes", new_column_name="notes")
    op.alter_column("cases", "summary_of_facts", new_column_name="facts")

    # Drop added columns
    op.drop_column("cases", "most_recent_activity_date")
    op.drop_column("cases", "most_recent_activity")
    op.drop_column("cases", "summary_of_significance")
    op.drop_column("cases", "published_opinions")
    op.drop_column("cases", "researcher")
    op.drop_column("cases", "current_jurisdiction")
    op.drop_column("cases", "jurisdiction_filed")
    op.drop_column("cases", "algorithm_list")
    op.drop_column("cases", "area_of_application_list")
    op.drop_column("cases", "issue_list")
