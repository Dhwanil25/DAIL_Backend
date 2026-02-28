"""
Caspio XLSX Migration Script

Reads existing Caspio data exports (Excel files) from the workspace and
imports them into the new PostgreSQL schema.

Run: python -m scripts.migrate_caspio

Expects XLSX files in the workspace root:
- Case_Table_*.xlsx
- Docket_Table_*.xlsx
- Document_Table_*.xlsx
- Secondary_Source_Coverage_Table_*.xlsx
"""

import asyncio
import glob
import os
import sys

import pandas as pd
from sqlalchemy import select

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import async_session_factory
from app.models.case import Case
from app.models.docket import Docket
from app.models.document import Document
from app.models.secondary_source import SecondarySource
from app.models.provenance import Provenance


def clean_row(row: dict) -> dict:
    """Replace NaN with None."""
    return {k: (None if pd.isna(v) else v) for k, v in row.items()}


async def import_cases(file_path: str):
    """Import cases from Caspio XLSX export."""
    print(f"Importing cases from: {file_path}")
    df = pd.read_excel(file_path)
    print(f"  Found {len(df)} rows")

    async with async_session_factory() as session:
        imported = 0
        skipped = 0

        for _, row in df.iterrows():
            data = clean_row(row.to_dict())

            # Map Caspio column names to model fields
            record_num = str(data.get("Record_Number", data.get("record_number", "")))
            if not record_num:
                skipped += 1
                continue

            # Check for existing
            result = await session.execute(
                select(Case).where(Case.record_number == record_num)
            )
            if result.scalar_one_or_none():
                skipped += 1
                continue

            case = Case(
                record_number=record_num,
                caption=data.get("Caption", data.get("caption", "Unknown")),
                case_slug=data.get("Case_Slug", data.get("case_slug")),
                brief_description=data.get("Brief_Description", data.get("brief_description")),
                facts=data.get("Facts", data.get("facts")),
                area_of_application=data.get("Area_of_Application", data.get("area_of_application")),
                issue_text=data.get("Issue", data.get("issue_text")),
                cause_of_action=data.get("Cause_of_Action", data.get("cause_of_action")),
                algorithm_name=data.get("Algorithm_Name", data.get("algorithm_name")),
                algorithm_description=data.get("Algorithm_Description", data.get("algorithm_description")),
                is_class_action=bool(data.get("Class_Action", data.get("is_class_action", False))),
                jurisdiction_name=data.get("Jurisdiction_Name", data.get("jurisdiction_name")),
                jurisdiction_type=data.get("Jurisdiction_Type", data.get("jurisdiction_type")),
                jurisdiction_state=data.get("Jurisdiction_State", data.get("jurisdiction_state")),
                jurisdiction_municipality=data.get("Jurisdiction_Municipality", data.get("jurisdiction_municipality")),
                status_disposition=data.get("Status_Disposition", data.get("status_disposition")),
                organizations_involved=data.get("Organizations_Involved", data.get("organizations_involved")),
                keywords=data.get("Keywords", data.get("keywords")),
                lead_case=data.get("Lead_Case", data.get("lead_case")),
                related_cases=data.get("Related_Cases", data.get("related_cases")),
                notes=data.get("Notes", data.get("notes")),
            )
            session.add(case)

            # Record provenance
            prov = Provenance(
                case_id=0,  # Will be set after flush
                source_system="caspio",
                source_identifier=record_num,
                ingestion_method="xlsx_import",
                notes=f"Migrated from {os.path.basename(file_path)}",
            )
            session.add(case)
            imported += 1

        await session.commit()
        print(f"  Cases: {imported} imported, {skipped} skipped")


async def import_dockets(file_path: str):
    """Import dockets from Caspio XLSX export."""
    print(f"Importing dockets from: {file_path}")
    df = pd.read_excel(file_path)
    print(f"  Found {len(df)} rows")

    async with async_session_factory() as session:
        imported = 0
        skipped = 0

        for _, row in df.iterrows():
            data = clean_row(row.to_dict())
            case_number = str(data.get("Case_Number", data.get("case_number", "")))

            # Find parent case
            result = await session.execute(
                select(Case).where(Case.record_number == case_number)
            )
            parent = result.scalar_one_or_none()
            if not parent:
                skipped += 1
                continue

            docket = Docket(
                case_id=parent.id,
                court_name=data.get("Court", data.get("court")),
                docket_number=data.get("Docket_Number", data.get("docket_number")),
                link=data.get("Link", data.get("link")),
            )
            session.add(docket)
            imported += 1

        await session.commit()
        print(f"  Dockets: {imported} imported, {skipped} skipped")


async def import_documents(file_path: str):
    """Import documents from Caspio XLSX export."""
    print(f"Importing documents from: {file_path}")
    df = pd.read_excel(file_path)
    print(f"  Found {len(df)} rows")

    async with async_session_factory() as session:
        imported = 0
        skipped = 0

        for _, row in df.iterrows():
            data = clean_row(row.to_dict())
            case_number = str(data.get("Case_Number", data.get("case_number", "")))

            result = await session.execute(
                select(Case).where(Case.record_number == case_number)
            )
            parent = result.scalar_one_or_none()
            if not parent:
                skipped += 1
                continue

            doc = Document(
                case_id=parent.id,
                document_title=data.get("Document_Title", data.get("document_title")),
                document_date=pd.to_datetime(
                    data.get("Document_Date", data.get("document_date")),
                    errors="coerce",
                ),
                cite_or_reference=data.get("Cite_or_Reference", data.get("cite_or_reference")),
                link=data.get("Link", data.get("link")),
            )
            session.add(doc)
            imported += 1

        await session.commit()
        print(f"  Documents: {imported} imported, {skipped} skipped")


async def import_secondary_sources(file_path: str):
    """Import secondary sources from Caspio XLSX export."""
    print(f"Importing secondary sources from: {file_path}")
    df = pd.read_excel(file_path)
    print(f"  Found {len(df)} rows")

    async with async_session_factory() as session:
        imported = 0
        skipped = 0

        for _, row in df.iterrows():
            data = clean_row(row.to_dict())
            case_number = str(data.get("Case_Number", data.get("case_number", "")))

            result = await session.execute(
                select(Case).where(Case.record_number == case_number)
            )
            parent = result.scalar_one_or_none()
            if not parent:
                skipped += 1
                continue

            source = SecondarySource(
                case_id=parent.id,
                title=data.get("Secondary_Source_Title", data.get("title")),
                link=data.get("Secondary_Source_Link", data.get("link")),
            )
            session.add(source)
            imported += 1

        await session.commit()
        print(f"  Secondary sources: {imported} imported, {skipped} skipped")


async def main():
    """Run full Caspio migration."""
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Workspace: {workspace}")
    print("=" * 60)

    # Find XLSX files
    case_files = glob.glob(os.path.join(workspace, "Case_Table_*.xlsx"))
    docket_files = glob.glob(os.path.join(workspace, "Docket_Table_*.xlsx"))
    doc_files = glob.glob(os.path.join(workspace, "Document_Table_*.xlsx"))
    source_files = glob.glob(os.path.join(workspace, "Secondary_Source_Coverage_Table_*.xlsx"))

    # Import in dependency order
    for f in case_files:
        await import_cases(f)

    for f in docket_files:
        await import_dockets(f)

    for f in doc_files:
        await import_documents(f)

    for f in source_files:
        await import_secondary_sources(f)

    print("=" * 60)
    print("Migration complete!")


if __name__ == "__main__":
    asyncio.run(main())
