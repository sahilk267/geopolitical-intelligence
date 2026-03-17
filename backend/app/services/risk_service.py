"""
Risk Governance Service
Shared logic for risk scoring used by APIs and background automation.
"""
import logging
from datetime import datetime
from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import NormalizedArticle
from app.models.risk import RiskScore
from app.core.config import settings

logger = logging.getLogger(__name__)


class RiskService:
    """Encapsulates risk scoring logic."""

    def analyze_content(self, article: NormalizedArticle) -> Dict[str, bool]:
        """Analyze raw text to detect risk factors."""
        headline = (article.headline or "").lower()
        summary = (article.summary or "").lower()
        content = f"{headline} {summary}".strip()
        tags = [t.lower() for t in (article.tags or [])]

        return {
            "named_individual": any(keyword in content for keyword in ["president", "minister", "leader", "mr.", "dr."]),
            "criminal_allegation": any(keyword in content for keyword in ["guilty", "crime", "corruption", "fraud"]),
            "single_anonymous_source": "anonymous" in content or "unnamed" in content,
            "war_topic": any(keyword in content for keyword in ["war", "attack", "strike", "military"]),
            "religious_framing": any(keyword in content for keyword in ["muslim", "islamic", "christian", "jewish"]),
            "israel_mentioned": "israel" in content or "israel" in tags,
            "iran_mentioned": "iran" in content or "iran" in tags,
            "palestine_mentioned": "palestine" in content or "palestine" in tags,
        }

    def calculate_scores(self, factors: Dict[str, bool]) -> Dict[str, int]:
        """Compute weighted scores for each dimension."""
        legal = 0
        defamation = 0
        platform = 0
        political = 0

        if factors["named_individual"]:
            legal += 15
            defamation += 20
            platform += 10
            political += 10
        if factors["criminal_allegation"]:
            legal += 25
            defamation += 30
            platform += 20
            political += 15
        if factors["single_anonymous_source"]:
            legal += 20
            defamation += 25
            platform += 15
        if factors["war_topic"]:
            platform += 25
            political += 20
        if factors["religious_framing"]:
            platform += 30
            political += 20
        if factors["israel_mentioned"] or factors["iran_mentioned"] or factors["palestine_mentioned"]:
            political += 15

        return {
            "legal": min(legal, 100),
            "defamation": min(defamation, 100),
            "platform": min(platform, 100),
            "political": min(political, 100),
        }

    def determine_safe_mode(self, factors: Dict[str, bool], safe_mode_enabled: bool) -> Dict[str, List[str]]:
        """Determine if safe mode blocks the content."""
        violations = []
        blocked = False

        if safe_mode_enabled:
            if factors["criminal_allegation"]:
                blocked = True
                violations.append("Criminal allegations not allowed in Safe Mode")
            if factors["war_topic"]:
                blocked = True
                violations.append("Active conflict analysis restricted in Safe Mode")

        return {"blocked": blocked, "violations": violations}

    def classify_overall(self, overall: int) -> str:
        """Map overall score to classification."""
        if overall > 80:
            return "Critical"
        if overall > 60:
            return "High"
        if overall > 40:
            return "Elevated"
        if overall > 20:
            return "Moderate"
        return "Low"

    async def assess_article(self, article: NormalizedArticle, assessed_by: str, db: AsyncSession, safe_mode_enabled: bool) -> RiskScore:
        """Create a risk score for the supplied article."""
        factors = self.analyze_content(article)
        scores = self.calculate_scores(factors)
        overall = round(
            scores["legal"] * 0.30 +
            scores["defamation"] * 0.30 +
            scores["platform"] * 0.20 +
            scores["political"] * 0.20
        )

        safe_mode = self.determine_safe_mode(factors, safe_mode_enabled)
        classification = self.classify_overall(overall)

        risk_score = RiskScore(
            article_id=article.id,
            legal_risk=scores["legal"],
            defamation_risk=scores["defamation"],
            platform_risk=scores["platform"],
            political_risk=scores["political"],
            overall_score=overall,
            classification=classification,
            risk_factors=factors,
            safe_mode_blocked=safe_mode["blocked"],
            safe_mode_violations=safe_mode["violations"] or None,
            requires_senior_review=overall > 40,
            assessed_by=assessed_by,
            assessed_at=datetime.utcnow(),
        )

        db.add(risk_score)
        await db.commit()
        await db.refresh(risk_score)

        logger.info(f"Created risk score {risk_score.id} for article {article.id} ({classification})")
        return risk_score


risk_service = RiskService()
