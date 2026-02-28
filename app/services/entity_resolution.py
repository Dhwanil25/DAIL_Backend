"""
Entity Resolution Service — name normalization and deduplication.

Implements a multi-stage pipeline for normalizing and matching
party names and judge names:
  normalize → block → match → cluster → merge/flag
"""

import re
import unicodedata
from typing import Optional

import structlog

logger = structlog.get_logger()


# ── Common legal entity suffixes ─────────────────────────────────────────
ENTITY_SUFFIXES = [
    r"\bInc\.?",
    r"\bCorp\.?",
    r"\bLLC\.?",
    r"\bL\.?L\.?C\.?",
    r"\bLLP\.?",
    r"\bL\.?L\.?P\.?",
    r"\bLtd\.?",
    r"\bCo\.?",
    r"\bPLC\.?",
    r"\bNA\b",
    r"\bN\.A\.?",
    r"\bet\s+al\.?",
    r"\bd/?b/?a\b",
]

# Compile entity suffix pattern
SUFFIX_PATTERN = re.compile(
    r"\s*,?\s*(?:" + "|".join(ENTITY_SUFFIXES) + r")\s*$",
    re.IGNORECASE,
)


class EntityResolutionService:
    """Service for normalizing and deduplicating entity names."""

    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize a party or judge name following CM/ECF conventions.

        Steps:
        1. Unicode normalization (NFKD)
        2. Strip leading/trailing whitespace
        3. Collapse multiple spaces
        4. Title case
        5. Remove common punctuation variations
        """
        if not name:
            return ""

        # Unicode normalize
        normalized = unicodedata.normalize("NFKD", name)

        # Strip and collapse spaces
        normalized = re.sub(r"\s+", " ", normalized.strip())

        # Remove excess punctuation but keep periods in abbreviations
        normalized = re.sub(r"[,;:]+\s*$", "", normalized)

        # Title case (but preserve known acronyms)
        normalized = normalized.title()

        # Restore common uppercase acronyms
        for acronym in ["LLC", "LLP", "PLC", "AI", "USA", "US", "FBI", "FTC", "SEC", "DOJ"]:
            normalized = re.sub(
                rf"\b{acronym.title()}\b", acronym, normalized
            )

        return normalized

    @staticmethod
    def extract_entity_suffix(name: str) -> tuple[str, Optional[str]]:
        """
        Separate entity name from legal suffix.
        Returns (base_name, suffix_or_none).
        """
        match = SUFFIX_PATTERN.search(name)
        if match:
            base = name[:match.start()].strip()
            suffix = match.group().strip().strip(",").strip()
            return base, suffix
        return name, None

    @staticmethod
    def compute_similarity(name_a: str, name_b: str) -> float:
        """
        Jaro-Winkler similarity between two names.
        Returns a score between 0.0 (no match) and 1.0 (exact match).
        """
        if not name_a or not name_b:
            return 0.0
        if name_a == name_b:
            return 1.0

        # Simple Jaro similarity implementation
        s1, s2 = name_a.lower(), name_b.lower()
        len_s1, len_s2 = len(s1), len(s2)

        max_dist = max(len_s1, len_s2) // 2 - 1
        if max_dist < 0:
            max_dist = 0

        s1_matches = [False] * len_s1
        s2_matches = [False] * len_s2

        matches = 0
        transpositions = 0

        for i in range(len_s1):
            start = max(0, i - max_dist)
            end = min(i + max_dist + 1, len_s2)

            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break

        if matches == 0:
            return 0.0

        k = 0
        for i in range(len_s1):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1

        jaro = (
            matches / len_s1
            + matches / len_s2
            + (matches - transpositions / 2) / matches
        ) / 3

        # Winkler modification — boost for common prefix
        prefix = 0
        for i in range(min(4, len_s1, len_s2)):
            if s1[i] == s2[i]:
                prefix += 1
            else:
                break

        return jaro + prefix * 0.1 * (1 - jaro)

    def find_matches(
        self,
        name: str,
        candidates: list[str],
        threshold: float = 0.85,
    ) -> list[tuple[str, float]]:
        """
        Find names from candidates that match above the threshold.
        Returns list of (candidate, similarity_score) tuples.
        """
        normalized = self.normalize_name(name)
        matches = []

        for candidate in candidates:
            norm_candidate = self.normalize_name(candidate)
            score = self.compute_similarity(normalized, norm_candidate)
            if score >= threshold:
                matches.append((candidate, score))

        return sorted(matches, key=lambda x: x[1], reverse=True)


# ── Singleton ────────────────────────────────────────────────────────────
_service: Optional[EntityResolutionService] = None


def get_entity_resolution_service() -> EntityResolutionService:
    global _service
    if _service is None:
        _service = EntityResolutionService()
    return _service
