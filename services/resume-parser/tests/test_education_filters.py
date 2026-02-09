"""Unit tests for education_filters utility module."""

import pytest
from unittest.mock import Mock, patch

from resume_parser.utils.education_filters import (
    EDUCATION_KEYWORDS,
    EDUCATION_PATTERNS,
    SKILL_KEYWORDS,
    is_educational_institution,
    classify_organization,
)


class TestIsEducationalInstitution:
    """Tests for is_educational_institution()."""

    def test_universities(self):
        assert is_educational_institution("University of Maryland") is True
        assert is_educational_institution("MIT University") is True
        assert is_educational_institution("Stanford University") is True

    def test_colleges(self):
        assert is_educational_institution("Data Science College Park") is True
        assert is_educational_institution("College of Engineering") is True

    def test_schools(self):
        assert is_educational_institution("Jefferson High School") is True

    def test_companies_are_not_educational(self):
        assert is_educational_institution("Google") is False
        assert is_educational_institution("Meta Platforms") is False
        assert is_educational_institution("TechCorp Inc.") is False

    def test_edge_cases(self):
        assert is_educational_institution("GPA") is True
        assert is_educational_institution("Portfolio Education") is True
        # Short / empty strings
        assert is_educational_institution("") is False
        assert is_educational_institution("A") is False
        assert is_educational_institution("   ") is False

    def test_pattern_matching(self):
        assert is_educational_institution("University of California") is True
        assert is_educational_institution("Bachelor of Science") is True
        assert is_educational_institution("Expected May 2025") is True


class TestClassifyOrganization:
    """Tests for classify_organization()."""

    def test_education_context(self):
        context = "Completed bachelor degree with 3.9 gpa, graduated with honors"
        assert classify_organization("Some Org", context) == "education"

    def test_employment_context(self):
        context = "Worked as a senior engineer and developer, built microservices"
        assert classify_organization("Some Org", context) == "employment"

    def test_by_name_overrides_context(self):
        # Even with employment context, a university name is classified as education
        context = "Worked as a software engineer developing applications"
        assert classify_organization("University of Maryland", context) == "education"

    def test_default_is_employment(self):
        assert classify_organization("Acme Corp", "") == "employment"
        assert classify_organization("Acme Corp", "neutral words here") == "employment"

    def test_empty_org(self):
        # Empty org name falls through to context analysis; education context wins
        assert classify_organization("", "bachelor gpa graduated") == "education"
        # With neutral context, defaults to employment
        assert classify_organization("", "some neutral words") == "employment"


class TestKeywordSets:
    """Verify the exported keyword sets are non-empty and well-formed."""

    def test_education_keywords_non_empty(self):
        assert len(EDUCATION_KEYWORDS) > 0
        assert all(kw == kw.lower() for kw in EDUCATION_KEYWORDS)

    def test_skill_keywords_non_empty(self):
        assert len(SKILL_KEYWORDS) > 0
        assert all(kw == kw.lower() for kw in SKILL_KEYWORDS)

    def test_education_patterns_non_empty(self):
        assert len(EDUCATION_PATTERNS) > 0


class TestIntegration:
    """Integration-level test: verify universities don't leak into companies."""

    def test_mixed_resume_filtering(self):
        """Universities in a resume should be flagged as educational."""
        entities = [
            "Google",
            "University of Maryland",
            "Meta Platforms",
            "College of Engineering",
            "TechCorp Inc.",
            "Jefferson High School",
        ]

        companies = [e for e in entities if not is_educational_institution(e)]
        educational = [e for e in entities if is_educational_institution(e)]

        assert "Google" in companies
        assert "Meta Platforms" in companies
        assert "TechCorp Inc." in companies

        assert "University of Maryland" in educational
        assert "College of Engineering" in educational
        assert "Jefferson High School" in educational

        # No educational institution should appear in companies
        for edu in educational:
            assert edu not in companies
