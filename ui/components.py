"""Reusable Streamlit UI components for StartupIQ."""

from __future__ import annotations

import html
from datetime import datetime

import streamlit as st

from agents.viability_scorer import ViabilityScoreResult
from ui.health import HealthScoreResult

# Navigation pages
NAV_DASHBOARD = "Dashboard"
NAV_DOCUMENTS = "Documents"
NAV_ANALYSIS = "Analysis"
NAV_REPORT = "Report"

NAV_OPTIONS = [NAV_DASHBOARD, NAV_DOCUMENTS, NAV_ANALYSIS, NAV_REPORT]

# Agent workflow definitions (order matters for status UI)
AGENT_WORKFLOW = [
    {"id": "rag", "name": "RAG Context Retrieval", "icon": "🔍"},
    {"id": "market", "name": "Market Research Agent", "icon": "📊"},
    {"id": "competitor", "name": "Competitor Analysis Agent", "icon": "⚔️"},
    {"id": "funding", "name": "Funding Advisor Agent", "icon": "💰"},
    {"id": "strategy", "name": "Business Strategy Agent", "icon": "🎯"},
    {"id": "viability", "name": "Viability Scoring", "icon": "📈"},
    {"id": "report", "name": "Report Generator Agent", "icon": "📋"},
]


def render_brand_hero(subtitle: str = "Multi-Agent Startup Intelligence Platform") -> None:
    """StartupIQ branded header banner."""
    st.markdown(
        f"""
        <div class="siq-hero">
            <span class="siq-badge">AI-Powered Intelligence</span>
            <h1>StartupIQ</h1>
            <p>{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_branding() -> None:
    """Compact logo block in the sidebar."""
    st.markdown(
        """
        <div style="text-align:center;padding:0.5rem 0 1rem 0;">
            <div style="font-size:1.5rem;font-weight:800;color:#A5B4FC;letter-spacing:-0.03em;">
                Startup<span style="color:#6366F1;">IQ</span>
            </div>
            <div style="font-size:0.7rem;color:#64748B;text-transform:uppercase;letter-spacing:0.1em;">
                Intelligence Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_nav() -> str:
    """Sidebar navigation radio; returns selected page name."""
    render_sidebar_branding()
    st.markdown("##### Navigate")
    page = st.radio(
        "Navigation",
        NAV_OPTIONS,
        label_visibility="collapsed",
        key="siq_nav_page",
    )
    st.divider()
    return page


def render_health_score(health: HealthScoreResult) -> None:
    """Display circular-style health score with tier badge."""
    score_class = ""
    if health.score < 40:
        score_class = "critical"
    elif health.score < 65:
        score_class = "warn"

    st.markdown(
        f"""
        <div class="siq-health-wrap">
            <div class="siq-metric-label">Startup Health Score</div>
            <div class="siq-health-score {score_class}">{health.score}</div>
            <div class="siq-health-label">out of 100</div>
            <span class="siq-health-tier">{html.escape(health.tier)}</span>
            <p style="color:#94A3B8;font-size:0.85rem;margin-top:1rem;margin-bottom:0;">
                {html.escape(health.summary)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_health_breakdown(health: HealthScoreResult) -> None:
    """Factor-by-factor score breakdown."""
    for label, points, note in health.factors:
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.caption(f"**{label}** — {note}")
        with col_b:
            st.caption(f"+{points} pts")


def render_metric_card(label: str, value: str, sub: str = "") -> None:
    """Single KPI metric card."""
    sub_html = f'<div class="siq-metric-sub">{html.escape(sub)}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="siq-metric-card">
            <div class="siq-metric-label">{html.escape(label)}</div>
            <div class="siq-metric-value">{html.escape(value)}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _status_label(status: str) -> str:
    labels = {
        "complete": "Complete",
        "running": "Running",
        "pending": "Pending",
        "error": "Failed",
    }
    return labels.get(status, status.title())


def render_agent_status_panel(agent_states: dict[str, str]) -> None:
    """
    Render live agent execution status rows.

    agent_states: mapping of agent id -> status (pending|running|complete|error)
    """
    st.markdown('<div class="siq-panel-title">Agent Execution Status</div>', unsafe_allow_html=True)
    for agent in AGENT_WORKFLOW:
        status = agent_states.get(agent["id"], "pending")
        st.markdown(
            f"""
            <div class="siq-agent-row {status}">
                <span class="siq-agent-dot {status}"></span>
                <span class="siq-agent-name">{agent["icon"]} {html.escape(agent["name"])}</span>
                <span class="siq-agent-status {status}">{_status_label(status)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def init_agent_states() -> dict[str, str]:
    """All workflow steps start as pending."""
    return {agent["id"]: "pending" for agent in AGENT_WORKFLOW}


def _viability_tier(score: int) -> str:
    if score >= 80:
        return "High Viability"
    if score >= 60:
        return "Moderate Viability"
    if score >= 40:
        return "Developing"
    return "High Risk"


def render_viability_score(viability: ViabilityScoreResult) -> None:
    """
    Display startup viability score (0–100) with progress bars and reasoning.

    Each dimension shows score, progress bar, and explanatory text.
    """
    tier = _viability_tier(viability.overall_score)

    st.markdown(
        f"""
        <div class="siq-panel">
            <div class="siq-panel-title">Startup Viability Score</div>
            <div style="display:flex;align-items:baseline;gap:0.75rem;margin-bottom:0.5rem;">
                <span style="font-size:2.25rem;font-weight:800;color:#A5B4FC;">{viability.overall_score}</span>
                <span style="color:#94A3B8;font-size:1rem;">/ 100</span>
                <span class="siq-health-tier">{html.escape(tier)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(viability.overall_score / 100, text=f"Overall viability: {viability.overall_score}%")
    st.markdown(f"**Summary:** {viability.summary}")

    st.markdown("##### Dimension Breakdown")
    for dim in viability.dimensions:
        st.markdown(f"**{dim.label}** — **{dim.score}/100**")
        st.progress(dim.score / 100)
        st.caption(dim.reasoning)
        st.markdown("")


def render_specialist_outputs_separate(outputs: list) -> None:
    """
    Display each specialist agent output in its own tab.

    Args:
        outputs: List of AgentOutput (or objects with agent_name and content).
    """
    if not outputs:
        st.caption("No agent outputs yet.")
        return

    labels = [o.agent_name.replace(" Agent", "") for o in outputs]
    tabs = st.tabs(labels)
    for tab, output in zip(tabs, outputs, strict=True):
        with tab:
            st.markdown(output.content)


def render_download_report(report_markdown: str, question: str) -> None:
    """Download button for the final intelligence report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"startupiq_report_{timestamp}.md"

    header = (
        f"# StartupIQ Intelligence Report\n\n"
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"**Question:** {question}\n\n---\n\n"
    )
    full_content = header + report_markdown

    st.download_button(
        label="⬇️ Download Report (.md)",
        data=full_content,
        file_name=filename,
        mime="text/markdown",
        type="primary",
        use_container_width=True,
    )
