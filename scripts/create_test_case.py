"""Quick script to create a test case and list all cases."""
import httpx
import json

BASE = "http://localhost:8000/api/v1"

test_case = {
    "record_number": "TEST-001",
    "caption": "Doe v. Clearview AI Inc.",
    "brief_description": "Plaintiff alleges Clearview AI violated BIPA by scraping facial images without consent.",
    "area_of_application": "Law Enforcement",
    "issue_text": "Whether mass facial recognition scraping violates Illinois BIPA",
    "cause_of_action": "Biometric Information Privacy Act",
    "algorithm_name": "Clearview AI Facial Recognition",
    "is_class_action": True,
    "jurisdiction_name": "U.S. District Court for the Northern District of Illinois",
    "jurisdiction_type": "federal",
    "jurisdiction_state": "IL",
    "status_disposition": "pending",
}

print("=== Creating test case ===")
r = httpx.post(f"{BASE}/cases", json=test_case)
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))

print("\n=== Listing all cases ===")
r = httpx.get(f"{BASE}/cases")
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))
