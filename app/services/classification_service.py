"""
AI Classification Service — automated case classification.

Implements a hybrid approach:
1. Rule-based keyword matching (immediate, high confidence)
2. NLP model classification (planned, with human-in-the-loop verification)

The rule-based system serves as the initial classifier; ML models
will be added as labeled training data accumulates from manual curation.
"""

import re
from typing import Optional

import structlog

logger = structlog.get_logger()


# ── Rule-Based Classification Patterns ───────────────────────────────────

AI_TECHNOLOGY_PATTERNS: dict[str, list[str]] = {
    "llm": [
        r"\bChatGPT\b", r"\bGPT[-\s]?[34]\b", r"\bGPT\b", r"\blarge language model\b",
        r"\bLLM\b", r"\bCopilot\b", r"\bLLaMA\b", r"\bClaude\b", r"\bGemini\b",
        r"\bBard\b", r"\bOpenAI\b", r"\bgenerative\s+AI\b", r"\bgen\s?AI\b",
    ],
    "computer_vision": [
        r"\bcomputer vision\b", r"\bimage recognition\b", r"\bobject detection\b",
        r"\bimage classification\b", r"\bvisual\s+AI\b",
    ],
    "facial_recognition": [
        r"\bfacial recognition\b", r"\bface\s+recognition\b", r"\bfaceprint\b",
        r"\bbiometric\s+(?:identification|surveillance)\b", r"\bClearview\b",
    ],
    "autonomous_vehicle": [
        r"\bautonomous\s+vehicle\b", r"\bself[-\s]?driving\b", r"\bautopilot\b",
        r"\bTesla\b.*\b(?:crash|accident|autopilot)\b", r"\bWaymo\b", r"\bCruise\b",
    ],
    "recommender_system": [
        r"\brecommend(?:ation|er)\s+(?:system|algorithm|engine)\b",
        r"\bcontent\s+(?:curation|moderation|recommendation)\b",
        r"\bnews\s+feed\s+algorithm\b",
    ],
    "hiring_algorithm": [
        r"\bhiring\s+algorithm\b", r"\bautomated\s+(?:hiring|screening|recruitment)\b",
        r"\bHireVue\b", r"\bapplicant\s+tracking\b", r"\bAI\s+hiring\b",
    ],
    "generative_ai": [
        r"\bgenerative\s+AI\b", r"\bDALL[-\s]?E\b", r"\bStable\s+Diffusion\b",
        r"\bMidjourney\b", r"\bAI[-\s]?generated\b", r"\bimage\s+generat\b",
        r"\btext[-\s]?to[-\s]?image\b",
    ],
    "medical_ai": [
        r"\bmedical\s+AI\b", r"\bclinical\s+decision\b", r"\bdiagnostic\s+AI\b",
        r"\bmedical\s+device\b.*\bAI\b", r"\bradiology\s+AI\b",
    ],
    "credit_scoring": [
        r"\bcredit\s+scor\b", r"\bcredit\s+decision\b", r"\blending\s+algorithm\b",
        r"\bautomated\s+(?:underwriting|credit)\b",
    ],
    "surveillance": [
        r"\bsurveillance\b.*\bAI\b", r"\bpredictive\s+polic\b",
        r"\bShotSpotter\b", r"\bPredPol\b", r"\bPalantir\b",
    ],
}

LEGAL_THEORY_PATTERNS: dict[str, list[str]] = {
    "copyright_infringement": [
        r"\bcopyright\s+infring\b", r"\bcopyright\s+violation\b",
        r"\bfair\s+use\b", r"\bcopyright\s+(?:claim|act|law)\b",
        r"\b17\s+U\.?S\.?C\b",
    ],
    "discrimination": [
        r"\bdiscriminat\b", r"\bbias\b", r"\bdisparate\s+impact\b",
        r"\bTitle\s+VII\b", r"\bequal\s+protection\b", r"\bADA\b",
    ],
    "privacy_violation": [
        r"\bprivacy\b", r"\bGDPR\b", r"\bCCPA\b", r"\bdata\s+breach\b",
        r"\bpersonal\s+data\b", r"\bdata\s+protection\b",
    ],
    "biometric_privacy": [
        r"\bBIPA\b", r"\bbiometric\s+(?:data|privacy|information)\b",
        r"\bIllinois\s+Biometric\b",
    ],
    "product_liability": [
        r"\bproduct\s+liability\b", r"\bdefective\s+product\b",
        r"\bstrict\s+liability\b", r"\bmanufacturing\s+defect\b",
    ],
    "securities_fraud": [
        r"\bsecurities\s+fraud\b", r"\bSEC\b.*\bAI\b", r"\bAI\s+washing\b",
        r"\b10b-5\b", r"\bsecurities\s+class\s+action\b",
    ],
    "consumer_protection": [
        r"\bconsumer\s+protection\b", r"\bFTC\b", r"\bunfair\s+(?:trade|business)\b",
        r"\bdeceptive\s+practice\b",
    ],
    "negligence": [
        r"\bnegligence\b", r"\bduty\s+of\s+care\b", r"\bmalpractice\b",
    ],
    "right_of_publicity": [
        r"\bright\s+of\s+publicity\b", r"\blikeness\b", r"\bpersonality\s+right\b",
    ],
    "professional_responsibility": [
        r"\bsanction\b.*\bAI\b", r"\bfabricated\s+citation\b",
        r"\bhallucin\b.*\blegal\b", r"\bMata\s+v\.\s+Avianca\b",
    ],
}

INDUSTRY_SECTOR_PATTERNS: dict[str, list[str]] = {
    "technology": [
        r"\bGoogle\b", r"\bMicrosoft\b", r"\bMeta\b", r"\bFacebook\b",
        r"\bAmazon\b", r"\bApple\b", r"\bOpenAI\b", r"\bAnthopic\b",
    ],
    "media_entertainment": [
        r"\bpublish\b", r"\bmusic\b", r"\bartist\b", r"\bauthor\b",
        r"\bwriter\b", r"\bcreative\b", r"\bholly?wood\b", r"\brecord\s+label\b",
    ],
    "healthcare": [
        r"\bhospital\b", r"\bpatient\b", r"\bhealthcare\b", r"\bmedical\b",
        r"\bpharmaceutical\b", r"\bFDA\b",
    ],
    "finance": [
        r"\bbank\b", r"\bfinancial\b", r"\binvestment\b", r"\binsurance\b",
        r"\bloan\b", r"\bcredit\b",
    ],
    "automotive": [
        r"\bTesla\b", r"\bWaymo\b", r"\bCruise\b", r"\bUber\b",
        r"\bautomotive\b", r"\bself[-\s]?driving\b",
    ],
    "employment": [
        r"\bhiring\b", r"\bemployment\b", r"\bworkplace\b", r"\brecruit\b",
        r"\bemployer\b", r"\bemployee\b",
    ],
    "law_enforcement": [
        r"\bpolice\b", r"\blaw\s+enforcement\b", r"\bprison\b",
        r"\bsentencing\b", r"\bcriminal\s+justice\b",
    ],
    "social_media": [
        r"\bsocial\s+media\b", r"\bTikTok\b", r"\bInstagram\b",
        r"\bTwitter\b", r"\bX\b.*\bplatform\b", r"\bYouTube\b",
    ],
}


class ClassificationService:
    """Hybrid rule-based + ML classification service."""

    def classify_case(
        self,
        caption: str,
        description: str = "",
        issues: str = "",
        cause_of_action: str = "",
    ) -> dict:
        """
        Classify a case across all dimensions.

        Returns dict with:
          - ai_technology_types: list of detected AI tech types
          - legal_theories: list of detected legal theories
          - industry_sectors: list of detected industry sectors
          - confidence_scores: dict of dimension -> confidence
        """
        combined_text = f"{caption} {description} {issues} {cause_of_action}"

        return {
            "ai_technology_types": self._match_patterns(
                combined_text, AI_TECHNOLOGY_PATTERNS
            ),
            "legal_theories": self._match_patterns(
                combined_text, LEGAL_THEORY_PATTERNS
            ),
            "industry_sectors": self._match_patterns(
                combined_text, INDUSTRY_SECTOR_PATTERNS
            ),
            "classification_source": "rule_based",
            "confidence_score": 0.7,  # Rule-based default confidence
        }

    def _match_patterns(
        self,
        text: str,
        patterns: dict[str, list[str]],
    ) -> list[str]:
        """Match text against a set of classification patterns."""
        matches = []
        for category, regex_patterns in patterns.items():
            for pattern in regex_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    if category not in matches:
                        matches.append(category)
                    break
        return matches


# ── Singleton ────────────────────────────────────────────────────────────
_service: Optional[ClassificationService] = None


def get_classification_service() -> ClassificationService:
    global _service
    if _service is None:
        _service = ClassificationService()
    return _service
