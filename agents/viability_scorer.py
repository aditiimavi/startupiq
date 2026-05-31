"""
Startup Viability Scorer — 0–100 assessment across four strategic dimensions.

Scores are derived from specialist agent analyses (market, competition,
funding, strategy) using Gemini with structured JSON output.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage

from agents.base import AgentOutput

SCORING_SYSTEM_PROMPT = """You are a startup viability analyst for StartupIQ.

Score the startup from 0–100 on each dimension using ONLY the specialist analyses provided.
Use integers 0–100. Be evidence-based; if data is missing, score conservatively and note gaps.

Dimensions:
1. market_potential — TAM/SAM, growth, demand, segment fit (100 = exceptional market opportunity)
2. competition_intensity — Score as COMPETITIVE POSITION: 100 = weak rivals / strong moat / clear differentiation;
   0 = hyper-competitive market with no defensible edge (inverse of raw intensity)
3. funding_readiness — investor readiness, metrics, stage-appropriate capital strategy (100 = highly fundable)
4. business_model_quality — revenue model, unit economics, GTM clarity (100 = robust, scalable model)

Return ONLY valid JSON (no markdown fences):
{
  "market_potential": {"score": <int>, "reasoning": "<1-3 sentences>"},
  "competition_intensity": {"score": <int>, "reasoning": "<1-3 sentences>"},
  "funding_readiness": {"score": <int>, "reasoning": "<1-3 sentences>"},
  "business_model_quality": {"score": <int>, "reasoning": "<1-3 sentences>"},
  "overall_summary": "<2-3 sentence synthesis of startup viability>"
}
"""


@dataclass
class DimensionScore:
    """Single viability dimension with score and explanation."""

    label: str
    score: int
    reasoning: str


@dataclass
class ViabilityScoreResult:
    """Complete startup viability assessment (0–100)."""

    overall_score: int
    market_potential: DimensionScore
    competition_intensity: DimensionScore
    funding_readiness: DimensionScore
    business_model_quality: DimensionScore
    summary: str

    @property
    def dimensions(self) -> list[DimensionScore]:
        """All four dimensions in display order."""
        return [
            self.market_potential,
            self.competition_intensity,
            self.funding_readiness,
            self.business_model_quality,
        ]


class ViabilityScorer:
    """Scores startup viability from specialist agent outputs."""

    def __init__(self, model_name: str = "gemini-2.0-flash", temperature: float = 0.2) -> None:
        import os

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set.")

        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
        )

    def score(
        self,
        question: str,
        market: AgentOutput,
        competitor: AgentOutput,
        funding: AgentOutput,
        strategy: AgentOutput,
    ) -> ViabilityScoreResult:
        """
        Compute viability scores from the four specialist analyses.

        Overall score is the rounded mean of the four dimension scores.
        """
        user_content = self._build_scoring_input(
            question, market, competitor, funding, strategy
        )
        messages = [
            SystemMessage(content=SCORING_SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]
        response = self.llm.invoke(messages)
        raw = response.content if isinstance(response.content, str) else str(response.content)
        parsed = _parse_json_response(raw)
        return _build_result(parsed)

    def _build_scoring_input(
        self,
        question: str,
        market: AgentOutput,
        competitor: AgentOutput,
        funding: AgentOutput,
        strategy: AgentOutput,
    ) -> str:
        return (
            f"## User Question\n{question}\n\n"
            f"## {market.agent_name}\n{market.content}\n\n"
            f"## {competitor.agent_name}\n{competitor.content}\n\n"
            f"## {funding.agent_name}\n{funding.content}\n\n"
            f"## {strategy.agent_name}\n{strategy.content}"
        )


def _parse_json_response(text: str) -> dict:
    """Extract JSON object from model response."""
    text = text.strip()
    # Strip markdown code fences if present
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not parse viability scores from model: {exc}") from exc


def _clamp_score(value: int) -> int:
    return max(0, min(100, int(value)))


def _extract_dimension(data: dict, key: str, label: str) -> DimensionScore:
    block = data.get(key, {})
    if not isinstance(block, dict):
        block = {}
    score = _clamp_score(block.get("score", 50))
    reasoning = str(block.get("reasoning", "Insufficient data to assess this dimension."))
    return DimensionScore(label=label, score=score, reasoning=reasoning)


def _build_result(parsed: dict) -> ViabilityScoreResult:
    market = _extract_dimension(parsed, "market_potential", "Market Potential")
    competition = _extract_dimension(
        parsed, "competition_intensity", "Competition Intensity"
    )
    funding = _extract_dimension(parsed, "funding_readiness", "Funding Readiness")
    business = _extract_dimension(
        parsed, "business_model_quality", "Business Model Quality"
    )

    scores = [market.score, competition.score, funding.score, business.score]
    overall = round(sum(scores) / len(scores))
    summary = str(
        parsed.get(
            "overall_summary",
            "Viability assessment based on multi-agent analysis.",
        )
    )

    return ViabilityScoreResult(
        overall_score=overall,
        market_potential=market,
        competition_intensity=competition,
        funding_readiness=funding,
        business_model_quality=business,
        summary=summary,
    )
