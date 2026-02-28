"""
Seed Courts Script

Populates the courts table with U.S. federal courts and major state courts.
Run: python -m scripts.seed_courts
"""

import asyncio
from sqlalchemy import select
from app.database import async_session_factory, engine, Base
from app.models.court import Court

FEDERAL_COURTS = [
    # Supreme Court
    {"name": "Supreme Court of the United States", "short_name": "SCOTUS", "citation_string": "U.S.", "courtlistener_id": "scotus", "jurisdiction_type": "federal", "court_level": "supreme"},
    # Circuit Courts of Appeals
    {"name": "U.S. Court of Appeals for the First Circuit", "short_name": "1st Cir.", "citation_string": "1st Cir.", "courtlistener_id": "ca1", "jurisdiction_type": "federal", "court_level": "appellate"},
    {"name": "U.S. Court of Appeals for the Second Circuit", "short_name": "2nd Cir.", "citation_string": "2d Cir.", "courtlistener_id": "ca2", "jurisdiction_type": "federal", "court_level": "appellate"},
    {"name": "U.S. Court of Appeals for the Third Circuit", "short_name": "3rd Cir.", "citation_string": "3d Cir.", "courtlistener_id": "ca3", "jurisdiction_type": "federal", "court_level": "appellate"},
    {"name": "U.S. Court of Appeals for the Fourth Circuit", "short_name": "4th Cir.", "citation_string": "4th Cir.", "courtlistener_id": "ca4", "jurisdiction_type": "federal", "court_level": "appellate"},
    {"name": "U.S. Court of Appeals for the Fifth Circuit", "short_name": "5th Cir.", "citation_string": "5th Cir.", "courtlistener_id": "ca5", "jurisdiction_type": "federal", "court_level": "appellate"},
    {"name": "U.S. Court of Appeals for the Sixth Circuit", "short_name": "6th Cir.", "citation_string": "6th Cir.", "courtlistener_id": "ca6", "jurisdiction_type": "federal", "court_level": "appellate"},
    {"name": "U.S. Court of Appeals for the Seventh Circuit", "short_name": "7th Cir.", "citation_string": "7th Cir.", "courtlistener_id": "ca7", "jurisdiction_type": "federal", "court_level": "appellate"},
    {"name": "U.S. Court of Appeals for the Eighth Circuit", "short_name": "8th Cir.", "citation_string": "8th Cir.", "courtlistener_id": "ca8", "jurisdiction_type": "federal", "court_level": "appellate"},
    {"name": "U.S. Court of Appeals for the Ninth Circuit", "short_name": "9th Cir.", "citation_string": "9th Cir.", "courtlistener_id": "ca9", "jurisdiction_type": "federal", "court_level": "appellate"},
    {"name": "U.S. Court of Appeals for the Tenth Circuit", "short_name": "10th Cir.", "citation_string": "10th Cir.", "courtlistener_id": "ca10", "jurisdiction_type": "federal", "court_level": "appellate"},
    {"name": "U.S. Court of Appeals for the Eleventh Circuit", "short_name": "11th Cir.", "citation_string": "11th Cir.", "courtlistener_id": "ca11", "jurisdiction_type": "federal", "court_level": "appellate"},
    {"name": "U.S. Court of Appeals for the D.C. Circuit", "short_name": "D.C. Cir.", "citation_string": "D.C. Cir.", "courtlistener_id": "cadc", "jurisdiction_type": "federal", "court_level": "appellate"},
    {"name": "U.S. Court of Appeals for the Federal Circuit", "short_name": "Fed. Cir.", "citation_string": "Fed. Cir.", "courtlistener_id": "cafc", "jurisdiction_type": "federal", "court_level": "appellate"},
    # Key District Courts
    {"name": "U.S. District Court for the Southern District of New York", "short_name": "S.D.N.Y.", "citation_string": "S.D.N.Y.", "courtlistener_id": "nysd", "jurisdiction_type": "federal", "court_level": "district", "state": "NY"},
    {"name": "U.S. District Court for the Northern District of California", "short_name": "N.D. Cal.", "citation_string": "N.D. Cal.", "courtlistener_id": "cand", "jurisdiction_type": "federal", "court_level": "district", "state": "CA"},
    {"name": "U.S. District Court for the Central District of California", "short_name": "C.D. Cal.", "citation_string": "C.D. Cal.", "courtlistener_id": "cacd", "jurisdiction_type": "federal", "court_level": "district", "state": "CA"},
    {"name": "U.S. District Court for the District of Columbia", "short_name": "D.D.C.", "citation_string": "D.D.C.", "courtlistener_id": "dcd", "jurisdiction_type": "federal", "court_level": "district", "state": "DC"},
    {"name": "U.S. District Court for the Eastern District of Virginia", "short_name": "E.D. Va.", "citation_string": "E.D. Va.", "courtlistener_id": "vaed", "jurisdiction_type": "federal", "court_level": "district", "state": "VA"},
    {"name": "U.S. District Court for the Northern District of Illinois", "short_name": "N.D. Ill.", "citation_string": "N.D. Ill.", "courtlistener_id": "ilnd", "jurisdiction_type": "federal", "court_level": "district", "state": "IL"},
    {"name": "U.S. District Court for the District of Delaware", "short_name": "D. Del.", "citation_string": "D. Del.", "courtlistener_id": "ded", "jurisdiction_type": "federal", "court_level": "district", "state": "DE"},
    {"name": "U.S. District Court for the Eastern District of Texas", "short_name": "E.D. Tex.", "citation_string": "E.D. Tex.", "courtlistener_id": "txed", "jurisdiction_type": "federal", "court_level": "district", "state": "TX"},
    {"name": "U.S. District Court for the Western District of Texas", "short_name": "W.D. Tex.", "citation_string": "W.D. Tex.", "courtlistener_id": "txwd", "jurisdiction_type": "federal", "court_level": "district", "state": "TX"},
]


async def seed_courts():
    """Insert courts, skipping duplicates by courtlistener_id."""
    async with async_session_factory() as session:
        inserted = 0
        skipped = 0
        for court_data in FEDERAL_COURTS:
            # Check for existing
            result = await session.execute(
                select(Court).where(
                    Court.courtlistener_id == court_data.get("courtlistener_id")
                )
            )
            if result.scalar_one_or_none():
                skipped += 1
                continue

            court = Court(**court_data)
            session.add(court)
            inserted += 1

        await session.commit()
        print(f"Courts seeded: {inserted} inserted, {skipped} skipped (already exist)")


if __name__ == "__main__":
    asyncio.run(seed_courts())
