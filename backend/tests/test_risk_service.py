import pytest

from app.models.article import NormalizedArticle
from app.services.risk_service import risk_service


def create_article(headline: str, summary: str, tags=None) -> NormalizedArticle:
    return NormalizedArticle(
        headline=headline,
        summary=summary,
        category="test",
        tags=tags or [],
    )


def test_analyze_content_detects_keywords():
    article = create_article(
        headline="President hints at military strike",
        summary="A minister mentioned war and corruption in an anonymous quote.",
        tags=["Israel"]
    )
    factors = risk_service.analyze_content(article)

    assert factors["named_individual"]
    assert factors["war_topic"]
    assert factors["criminal_allegation"]
    assert factors["israel_mentioned"]


def test_calculate_scores_caps_at_hundred():
    factors = {
        "named_individual": True,
        "criminal_allegation": True,
        "single_anonymous_source": True,
        "war_topic": True,
        "religious_framing": True,
        "israel_mentioned": True,
        "iran_mentioned": False,
        "palestine_mentioned": False,
    }
    scores = risk_service.calculate_scores(factors)

    assert scores["legal"] <= 100
    assert scores["defamation"] <= 100
    assert scores["platform"] <= 100
    assert scores["political"] <= 100
    assert scores["legal"] > 0
    assert scores["defamation"] > 0


def test_safe_mode_violation_flags():
    factors = {
        "named_individual": False,
        "criminal_allegation": True,
        "single_anonymous_source": False,
        "war_topic": True,
        "religious_framing": False,
        "israel_mentioned": False,
        "iran_mentioned": False,
        "palestine_mentioned": False,
    }
    safe_mode = risk_service.determine_safe_mode(factors, safe_mode_enabled=True)

    assert safe_mode["blocked"]
    assert "Criminal allegations not allowed" in safe_mode["violations"][0]
    assert "Active conflict analysis restricted" in safe_mode["violations"][1]
