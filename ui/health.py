"""Startup Health Score — composite readiness metric for the dashboard."""

from dataclasses import dataclass

from agents.base import AgentOutput


@dataclass
class HealthScoreResult:
    """Health score breakdown and display metadata."""

    score: int
    tier: str
    summary: str
    factors: list[tuple[str, int, str]]  # label, points, note


def compute_health_score(
    indexed: bool,
    chunk_count: int,
    has_report: bool,
    specialist_outputs: list[AgentOutput] | None,
    uploaded_file_count: int = 0,
) -> HealthScoreResult:
    """
    Compute a 0–100 Startup Health Score from platform state and analysis depth.

    Scoring dimensions:
        - Document pipeline (indexing, chunk depth)
        - Knowledge base coverage
        - Multi-agent analysis completion
        - Report availability
    """
    factors: list[tuple[str, int, str]] = []
    total = 0

    # Document ingestion
    if indexed:
        pts = 20
        note = "Documents indexed in vector store"
    elif uploaded_file_count > 0:
        pts = 8
        note = "PDFs uploaded — index to unlock full score"
    else:
        pts = 0
        note = "No documents indexed yet"
    factors.append(("Document Pipeline", pts, note))
    total += pts

    # Chunk depth (proxy for RAG coverage)
    if chunk_count >= 20:
        pts, note = 25, f"Strong coverage ({chunk_count} chunks)"
    elif chunk_count >= 8:
        pts, note = 18, f"Moderate coverage ({chunk_count} chunks)"
    elif chunk_count >= 1:
        pts, note = 10, f"Limited coverage ({chunk_count} chunks)"
    else:
        pts, note = 0, "No embedded chunks"
    factors.append(("Knowledge Base", pts, note))
    total += pts

    # Specialist agent completion
    completed = len(specialist_outputs or [])
    if completed >= 4:
        pts, note = 30, "All specialist agents completed"
    elif completed >= 1:
        pts = completed * 6
        note = f"{completed}/4 specialist analyses done"
    else:
        pts, note = 0, "Run analysis to activate agents"
    factors.append(("Agent Analysis", pts, note))
    total += pts

    # Final report
    if has_report:
        pts, note = 25, "Intelligence report generated"
    else:
        pts, note = 0, "No report yet"
    factors.append(("Intelligence Report", pts, note))
    total += pts

    score = min(100, total)
    tier, summary = _tier_for_score(score)
    return HealthScoreResult(score=score, tier=tier, summary=summary, factors=factors)


def _tier_for_score(score: int) -> tuple[str, str]:
    if score >= 85:
        return "Excellent", "Startup intelligence pipeline is fully operational."
    if score >= 65:
        return "Good", "Strong foundation — refine documents or re-run analysis for deeper insights."
    if score >= 40:
        return "Fair", "Partial readiness — index more documents and complete a full analysis."
    if score >= 20:
        return "Needs Attention", "Early stage — upload PDFs and run your first multi-agent analysis."
    return "Critical", "Get started by uploading startup documents and indexing them."
