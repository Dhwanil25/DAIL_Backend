"""Quick test: fetch Authors Guild v. OpenAI from CourtListener and enrich our DAIL case."""
import asyncio
import json
from datetime import date

def parse_date(val):
    """Parse a date string from CourtListener API into a date object."""
    if val and isinstance(val, str):
        return date.fromisoformat(val)
    return None

async def test():
    from app.services.courtlistener import get_courtlistener_client
    from app.database import async_session_factory
    from app.models.docket import Docket
    from sqlalchemy import select

    client = get_courtlistener_client()

    # 1) Fetch docket details from CourtListener
    print("=== Fetching Docket 69459176 from CourtListener ===")
    docket = await client.get_docket(69459176)

    fields = [
        "case_name", "docket_number", "court", "date_filed",
        "date_terminated", "nature_of_suit", "cause",
        "pacer_case_id", "assigned_to_str", "jurisdiction_type",
    ]
    for f in fields:
        print(f"  {f}: {docket.get(f)}")

    # 2) Store as a docket linked to our test case (id=3)
    print("\n=== Creating DAIL Docket from CourtListener data ===")
    async with async_session_factory() as session:
        # Check if docket already exists
        existing = await session.execute(
            select(Docket).where(Docket.courtlistener_docket_id == 69459176)
        )
        if existing.scalar_one_or_none():
            print("Docket already exists, skipping insert.")
        else:
            court_url = docket.get("court", "")
            new_docket = Docket(
                case_id=3,
                docket_number=docket.get("docket_number"),
                courtlistener_docket_id=69459176,
                courtlistener_url=f"https://www.courtlistener.com/docket/69459176/authors-guild-v-openai-inc/",
                pacer_case_id=docket.get("pacer_case_id"),
                court_name=docket.get("assigned_to_str", ""),
                date_filed=parse_date(docket.get("date_filed")),
                date_terminated=parse_date(docket.get("date_terminated")),
                nature_of_suit=docket.get("nature_of_suit"),
                plaintiff_summary="Authors Guild",
                defendant_summary="OpenAI Inc.",
            )
            session.add(new_docket)
            await session.commit()
            print(f"Created docket id={new_docket.id}")

    # 3) Search for related opinions
    print("\n=== Searching CourtListener Opinions ===")
    opinions = await client.search_opinions(query="Authors Guild v. OpenAI")
    for op in opinions.get("results", [])[:5]:
        print(f"  [{op.get('dateFiled')}] {op.get('caseName')} ({op.get('court')})")

    # 4) Verify the full case now in our API
    print("\n=== Verifying DAIL Case 3 now has docket ===")
    async with async_session_factory() as session:
        from app.models.case import Case
        from sqlalchemy.orm import selectinload
        result = await session.execute(
            select(Case)
            .options(selectinload(Case.dockets))
            .where(Case.id == 3)
        )
        case = result.scalar_one()
        print(f"Case: {case.caption}")
        print(f"Dockets: {len(case.dockets)}")
        for d in case.dockets:
            print(f"  - #{d.docket_number} (CL:{d.courtlistener_docket_id}) filed {d.date_filed}")

    print("\nDone!")

asyncio.run(test())
