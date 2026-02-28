"""
CourtListener Import Script

Fetches AI-related dockets from CourtListener and creates/enriches
DAIL case records.

Run: python -m scripts.import_courtlistener

Requires COURTLISTENER_API_TOKEN environment variable.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.courtlistener import get_courtlistener_client


AI_KEYWORDS = [
    "artificial intelligence",
    "machine learning",
    "facial recognition",
    "algorithmic bias",
    "automated decision",
    "ChatGPT",
    "generative AI",
    "deepfake",
    "autonomous vehicle",
    "predictive policing",
]


async def search_ai_dockets():
    """Search CourtListener for AI-related dockets."""
    client = get_courtlistener_client()
    all_dockets = []

    for keyword in AI_KEYWORDS:
        print(f"Searching for: {keyword}")
        try:
            results = await client.search_dockets(
                query=keyword,
                date_filed_after="2020-01-01",
            )
            hits = results.get("results", [])
            all_dockets.extend(hits)
            print(f"  Found {len(hits)} dockets")
        except Exception as e:
            print(f"  Error: {e}")

    # Deduplicate by docket ID
    seen = set()
    unique = []
    for d in all_dockets:
        did = d.get("id")
        if did and did not in seen:
            seen.add(did)
            unique.append(d)

    print(f"\nTotal unique dockets found: {len(unique)}")
    return unique


async def main():
    """Run CourtListener import pipeline."""
    print("CourtListener Import Script")
    print("=" * 60)

    if not os.environ.get("COURTLISTENER_API_TOKEN"):
        print("ERROR: COURTLISTENER_API_TOKEN environment variable not set")
        print("Get a token at: https://www.courtlistener.com/api/rest-info/")
        sys.exit(1)

    dockets = await search_ai_dockets()

    print(f"\nFound {len(dockets)} AI-related dockets on CourtListener")
    print("To enrich these in DAIL, use the API or Celery tasks:")
    print("  POST /api/v1/cases with CourtListener docket URL")
    print("  or: celery call app.tasks.ingestion_tasks.enrich_case_from_courtlistener")

    # Print sample dockets
    for d in dockets[:10]:
        print(f"  - [{d.get('id')}] {d.get('case_name', 'Unknown')}")

    if len(dockets) > 10:
        print(f"  ... and {len(dockets) - 10} more")


if __name__ == "__main__":
    asyncio.run(main())
