"""
Tests for the classification and entity resolution services.
"""

import pytest


class TestClassificationService:
    """Test rule-based classification patterns."""

    def test_detect_facial_recognition(self):
        from app.services.classification_service import get_classification_service

        service = get_classification_service()
        result = service.classify_case(
            caption="Doe v. Clearview AI",
            description="Facial recognition biometric data collection",
            issues="BIPA violation facial recognition",
            cause_of_action="BIPA",
        )
        assert "facial_recognition" in result["ai_technology_types"]

    def test_detect_algorithmic_hiring(self):
        from app.services.classification_service import get_classification_service

        service = get_classification_service()
        result = service.classify_case(
            caption="EEOC v. TechCorp",
            description="Algorithmic hiring tool discriminated against applicants",
            issues="Title VII disparate impact",
            cause_of_action="Title VII",
        )
        assert "algorithmic_hiring" in result["ai_technology_types"]

    def test_detect_generative_ai(self):
        from app.services.classification_service import get_classification_service

        service = get_classification_service()
        result = service.classify_case(
            caption="Author v. OpenAI",
            description="ChatGPT used copyrighted works for training",
            issues="Copyright infringement",
            cause_of_action="Copyright Act",
        )
        assert "generative_ai" in result["ai_technology_types"]

    def test_detect_legal_theories(self):
        from app.services.classification_service import get_classification_service

        service = get_classification_service()
        result = service.classify_case(
            caption="Privacy Lawsuit",
            description="Fourth Amendment unreasonable search using AI surveillance",
            issues="Due process violation algorithmic sentencing",
            cause_of_action="Section 1983",
        )
        assert any(
            t in result["legal_theories"]
            for t in ["constitutional_rights", "due_process"]
        )


class TestEntityResolution:
    """Test name normalization and similarity matching."""

    def test_normalize_name(self):
        from app.services.entity_resolution import get_entity_resolution_service

        service = get_entity_resolution_service()
        assert service.normalize_name("  JOHN   DOE  ") == "John Doe"

    def test_strip_suffix(self):
        from app.services.entity_resolution import get_entity_resolution_service

        service = get_entity_resolution_service()
        name, suffix = service.extract_entity_suffix("Acme Corp Inc.")
        assert suffix == "Inc."

    def test_similarity_matching(self):
        from app.services.entity_resolution import get_entity_resolution_service

        service = get_entity_resolution_service()
        score = service.compute_similarity("John Smith", "John Smyth")
        assert score > 0.8
