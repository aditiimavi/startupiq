"""Report Generator Agent — merges specialist outputs into a unified intelligence report."""

from agents.base import AgentOutput, BaseAgent


class ReportGeneratorAgent(BaseAgent):
    """
    Synthesizes independent agent analyses into one cohesive executive report.

    This is the only agent that sees all other agents' outputs.
    """

    agent_name = "Report Generator Agent"
    system_prompt = """You are the Report Generator Agent for StartupIQ.

You receive analyses from specialist agents (Market Research, Competitor Analysis,
Funding Advisor, Business Strategy) plus the original user question and document context.

Your job:
- Merge insights into a single, polished **Startup Intelligence Report**
- Resolve contradictions between agents and note uncertainty
- Prioritize the most actionable insights for founders and investors
- Keep a professional, executive-ready tone
- Do not invent facts; attribute themes to the specialist sections

Required report structure:

# StartupIQ Intelligence Report

## 1. Executive Summary
(High-level answer to the user's question in 1–2 paragraphs)

## 2. Key Findings
(Bulleted synthesis across all domains)

## 3. Market & Customers
(Distilled from Market Research)

## 4. Competitive Position
(Distilled from Competitor Analysis)

## 5. Funding & Financial Outlook
(Distilled from Funding Advisor)

## 6. Strategic Roadmap
(Distilled from Business Strategy)

## 7. Unified Recommendations
(Top 5–7 prioritized actions)

## 8. Appendix: Analyst Notes
(Brief mention of data gaps or conflicting views)

Use markdown headings exactly as shown."""

    def generate(
        self,
        question: str,
        context: str,
        specialist_outputs: list[AgentOutput],
    ) -> AgentOutput:
        """Combine specialist agent outputs into the final report."""
        sections = []
        for output in specialist_outputs:
            sections.append(f"### {output.agent_name}\n\n{output.content}")

        combined_analyses = "\n\n---\n\n".join(sections)
        enriched_context = (
            f"{context}\n\n"
            f"## Specialist Agent Analyses\n\n{combined_analyses}"
        )
        return self.analyze(question, enriched_context)
