"""
DAIL Backend - Database Models Package

All models are imported here so Alembic and the app can discover them.
"""

from app.models.court import Court
from app.models.case import Case
from app.models.docket import Docket
from app.models.opinion import OpinionCluster, Opinion
from app.models.citation import Citation
from app.models.party import Party, CaseParty
from app.models.judge import Judge, CaseJudge
from app.models.document import Document
from app.models.secondary_source import SecondarySource
from app.models.ai_classification import AIClassification
from app.models.audit import AuditLog
from app.models.provenance import Provenance

__all__ = [
    "Court",
    "Case",
    "Docket",
    "OpinionCluster",
    "Opinion",
    "Citation",
    "Party",
    "CaseParty",
    "Judge",
    "CaseJudge",
    "Document",
    "SecondarySource",
    "AIClassification",
    "AuditLog",
    "Provenance",
]
