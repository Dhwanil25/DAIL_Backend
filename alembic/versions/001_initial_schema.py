"""Initial DAIL Schema

Revision ID: 001
Revises: None
Create Date: 2025-01-01 00:00:00.000000

Creates all tables for the Database of AI Litigation backend.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Courts ---
    op.create_table(
        "courts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("short_name", sa.String(100)),
        sa.Column("citation_string", sa.String(100)),
        sa.Column("courtlistener_id", sa.String(50), unique=True),
        sa.Column("pacer_id", sa.String(10)),
        sa.Column("jurisdiction_type", sa.String(50)),
        sa.Column("court_level", sa.String(50)),
        sa.Column("state", sa.String(2)),
        sa.Column("country", sa.String(100), server_default="US"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- Cases ---
    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("record_number", sa.String(50), unique=True, nullable=False),
        sa.Column("caption", sa.Text(), nullable=False),
        sa.Column("case_slug", sa.String(255)),
        sa.Column("brief_description", sa.Text()),
        sa.Column("facts", sa.Text()),
        sa.Column("area_of_application", sa.String(255)),
        sa.Column("issue_text", sa.Text()),
        sa.Column("cause_of_action", sa.Text()),
        sa.Column("algorithm_name", sa.String(500)),
        sa.Column("algorithm_description", sa.Text()),
        sa.Column("is_class_action", sa.Boolean(), server_default="false"),
        sa.Column("jurisdiction_name", sa.String(255)),
        sa.Column("jurisdiction_type", sa.String(100)),
        sa.Column("jurisdiction_state", sa.String(100)),
        sa.Column("jurisdiction_municipality", sa.String(255)),
        sa.Column("status_disposition", sa.String(100)),
        sa.Column("filed_date", sa.Date()),
        sa.Column("closed_date", sa.Date()),
        sa.Column("organizations_involved", sa.Text()),
        sa.Column("keywords", sa.Text()),
        sa.Column("lead_case", sa.String(50)),
        sa.Column("related_cases", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("last_updated_by", sa.String(100)),
        sa.Column("ai_technology_types", JSONB),
        sa.Column("legal_theories", JSONB),
        sa.Column("industry_sectors", JSONB),
        sa.Column("search_vector", TSVECTOR),
        sa.Column("is_deleted", sa.Boolean(), server_default="false"),
        sa.Column("version", sa.Integer(), server_default="1"),
        sa.Column("superseded_by_id", sa.Integer(), sa.ForeignKey("cases.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_cases_search_vector", "cases", ["search_vector"], postgresql_using="gin")
    op.create_index("ix_cases_ai_tech", "cases", ["ai_technology_types"], postgresql_using="gin")
    op.create_index("ix_cases_legal_theories", "cases", ["legal_theories"], postgresql_using="gin")
    op.create_index("ix_cases_status", "cases", ["status_disposition"])
    op.create_index("ix_cases_filed_date", "cases", ["filed_date"])

    # --- Dockets ---
    op.create_table(
        "dockets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("court_id", sa.Integer(), sa.ForeignKey("courts.id")),
        sa.Column("docket_number", sa.String(100)),
        sa.Column("courtlistener_docket_id", sa.Integer(), unique=True),
        sa.Column("courtlistener_url", sa.Text()),
        sa.Column("pacer_case_id", sa.String(50)),
        sa.Column("court_name", sa.String(500)),
        sa.Column("date_filed", sa.Date()),
        sa.Column("date_terminated", sa.Date()),
        sa.Column("nature_of_suit", sa.String(500)),
        sa.Column("plaintiff_summary", sa.Text()),
        sa.Column("defendant_summary", sa.Text()),
        sa.Column("link", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- Opinion Clusters ---
    op.create_table(
        "opinion_clusters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("docket_id", sa.Integer(), sa.ForeignKey("dockets.id")),
        sa.Column("courtlistener_cluster_id", sa.Integer(), unique=True),
        sa.Column("case_name", sa.Text()),
        sa.Column("date_filed", sa.Date()),
        sa.Column("syllabus", sa.Text()),
        sa.Column("procedural_history", sa.Text()),
        sa.Column("judges", sa.Text()),
        sa.Column("citation_count", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- Opinions ---
    op.create_table(
        "opinions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("opinion_clusters.id"), nullable=False),
        sa.Column("courtlistener_opinion_id", sa.Integer(), unique=True),
        sa.Column("opinion_type", sa.String(50)),
        sa.Column("author_str", sa.String(500)),
        sa.Column("plain_text", sa.Text()),
        sa.Column("html", sa.Text()),
        sa.Column("html_with_citations", sa.Text()),
        sa.Column("word_count", sa.Integer()),
        sa.Column("search_vector", TSVECTOR),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_opinions_search_vector", "opinions", ["search_vector"], postgresql_using="gin")

    # --- Citations ---
    op.create_table(
        "citations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("citing_case_id", sa.Integer(), sa.ForeignKey("cases.id")),
        sa.Column("cited_case_id", sa.Integer(), sa.ForeignKey("cases.id")),
        sa.Column("citing_opinion_id", sa.Integer(), sa.ForeignKey("opinions.id")),
        sa.Column("cited_opinion_id", sa.Integer(), sa.ForeignKey("opinions.id")),
        sa.Column("citation_type", sa.String(50)),
        sa.Column("citation_text", sa.Text(), nullable=False),
        sa.Column("volume", sa.String(20)),
        sa.Column("reporter", sa.String(100)),
        sa.Column("page", sa.String(20)),
        sa.Column("pin_cite", sa.String(50)),
        sa.Column("year", sa.Integer()),
        sa.Column("court_cite", sa.String(100)),
        sa.Column("plaintiff_name", sa.String(500)),
        sa.Column("defendant_name", sa.String(500)),
        sa.Column("depth", sa.Integer(), server_default="1"),
        sa.Column("courtlistener_verified", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_citations_reporter", "citations", ["reporter", "volume", "page"])

    # --- Parties ---
    op.create_table(
        "parties",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(1000), nullable=False),
        sa.Column("name_normalized", sa.String(1000)),
        sa.Column("party_type", sa.String(50)),
        sa.Column("canonical_id", sa.Integer(), sa.ForeignKey("parties.id")),
        sa.Column("is_alias", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_parties_name_normalized", "parties", ["name_normalized"])

    # --- Case Parties (junction) ---
    op.create_table(
        "case_parties",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("party_id", sa.Integer(), sa.ForeignKey("parties.id"), nullable=False),
        sa.Column("role", sa.String(50)),
        sa.Column("attorney_name", sa.String(500)),
        sa.Column("attorney_firm", sa.String(500)),
    )

    # --- Judges ---
    op.create_table(
        "judges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("name_normalized", sa.String(500)),
        sa.Column("courtlistener_person_id", sa.Integer(), unique=True),
        sa.Column("position_title", sa.String(255)),
        sa.Column("court_name", sa.String(500)),
        sa.Column("appointed_by", sa.String(500)),
        sa.Column("canonical_id", sa.Integer(), sa.ForeignKey("judges.id")),
        sa.Column("is_alias", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- Case Judges (junction) ---
    op.create_table(
        "case_judges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("judge_id", sa.Integer(), sa.ForeignKey("judges.id"), nullable=False),
        sa.Column("role", sa.String(50)),
    )

    # --- Documents ---
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("docket_id", sa.Integer(), sa.ForeignKey("dockets.id")),
        sa.Column("document_type", sa.String(50)),
        sa.Column("document_title", sa.Text()),
        sa.Column("document_date", sa.Date()),
        sa.Column("cite_or_reference", sa.Text()),
        sa.Column("link", sa.Text()),
        sa.Column("courtlistener_recap_id", sa.Integer()),
        sa.Column("pacer_doc_id", sa.String(50)),
        sa.Column("page_count", sa.Integer()),
        sa.Column("extracted_text", sa.Text()),
        sa.Column("storage_url", sa.Text()),
        sa.Column("file_size_bytes", sa.BigInteger()),
        sa.Column("mime_type", sa.String(100)),
        sa.Column("search_vector", TSVECTOR),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_documents_search_vector", "documents", ["search_vector"], postgresql_using="gin")

    # --- Secondary Sources ---
    op.create_table(
        "secondary_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("title", sa.Text()),
        sa.Column("link", sa.Text()),
        sa.Column("source_name", sa.String(500)),
        sa.Column("author", sa.String(500)),
        sa.Column("publication_date", sa.Date()),
        sa.Column("source_type", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- AI Classifications ---
    op.create_table(
        "ai_classifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("ai_technology_type", sa.String(100)),
        sa.Column("legal_theory", sa.String(100)),
        sa.Column("industry_sector", sa.String(100)),
        sa.Column("classification_source", sa.String(50)),
        sa.Column("confidence_score", sa.Float()),
        sa.Column("classified_by", sa.String(100)),
        sa.Column("verified_by", sa.String(100)),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- Audit Log ---
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("table_name", sa.String(100), nullable=False),
        sa.Column("record_id", sa.Integer()),
        sa.Column("old_values", JSONB),
        sa.Column("new_values", JSONB),
        sa.Column("changed_fields", JSONB),
        sa.Column("changed_by", sa.String(100)),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("request_id", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_log_table_record", "audit_log", ["table_name", "record_id"])
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])

    # --- Provenance ---
    op.create_table(
        "provenance",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("source_system", sa.String(50), nullable=False),
        sa.Column("source_url", sa.Text()),
        sa.Column("source_identifier", sa.String(255)),
        sa.Column("ingestion_method", sa.String(50)),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("processing_steps", JSONB),
        sa.Column("confidence_score", sa.Float()),
        sa.Column("notes", sa.Text()),
    )

    # --- Full-text search trigger for cases ---
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
                setweight(to_tsvector('english', coalesce(NEW.facts, '')), 'D');
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trig_cases_search_vector
        BEFORE INSERT OR UPDATE ON cases
        FOR EACH ROW EXECUTE FUNCTION update_case_search_vector();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trig_cases_search_vector ON cases;")
    op.execute("DROP FUNCTION IF EXISTS update_case_search_vector();")
    op.drop_table("provenance")
    op.drop_table("audit_log")
    op.drop_table("ai_classifications")
    op.drop_table("secondary_sources")
    op.drop_table("documents")
    op.drop_table("case_judges")
    op.drop_table("judges")
    op.drop_table("case_parties")
    op.drop_table("parties")
    op.drop_table("citations")
    op.drop_table("opinions")
    op.drop_table("opinion_clusters")
    op.drop_table("dockets")
    op.drop_table("cases")
    op.drop_table("courts")
