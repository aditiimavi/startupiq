from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass

from langchain_core.documents import Document

from agents.base import AgentOutput
from agents.business_strategy import BusinessStrategyAgent
from agents.competitor_analysis import CompetitorAnalysisAgent
from agents.funding_advisor import FundingAdvisorAgent
from agents.market_research import MarketResearchAgent
from agents.report_generator import ReportGeneratorAgent
from agents.viability_scorer import ViabilityScoreResult, ViabilityScorer
from rag.retriever import RAGPipeline

ProgressCallback = Callable[[str, str], None]

STEP_RAG = "rag"
STEP_MARKET = "market"
STEP_COMPETITOR = "competitor"
STEP_FUNDING = "funding"
STEP_STRATEGY = "strategy"
STEP_VIABILITY = "viability"
STEP_REPORT = "report"

@dataclass
class WorkflowResult:
    question: str
    context: str
    market: AgentOutput
    competitor: AgentOutput
    funding: AgentOutput
    strategy: AgentOutput
    final_report: AgentOutput
    viability: ViabilityScoreResult
    source_documents: list[Document]

@property
def specialist_outputs(self):
    return [
        self.market,
        self.competitor,
        self.funding,
        self.strategy,
    ]


class StartupIQOrchestrator:
    """
    Coordinates the complete StartupIQ workflow.
    """

    def __init__(self, rag_pipeline: RAGPipeline | None = None):
        self.rag = rag_pipeline or RAGPipeline()

    def run(
        self,
        question: str,
        on_progress: ProgressCallback | None = None,
    ) -> WorkflowResult:

        question = question.strip()

        if not question:
            raise ValueError("Question cannot be empty.")

        # ------------------------
        # RAG Retrieval
        # ------------------------
        context, source_documents = self._retrieve_context(
            question,
            on_progress,
        )

        if not context:
            context = "No relevant context found."

        # ------------------------
        # Specialist Agents
        # ------------------------
        market = self._run_agent(
            STEP_MARKET,
            MarketResearchAgent(),
            question,
            context,
            on_progress,
        )

        competitor = self._run_agent(
            STEP_COMPETITOR,
            CompetitorAnalysisAgent(),
            question,
            context,
            on_progress,
        )

        funding = self._run_agent(
            STEP_FUNDING,
            FundingAdvisorAgent(),
            question,
            context,
            on_progress,
        )

        strategy = self._run_agent(
            STEP_STRATEGY,
            BusinessStrategyAgent(),
            question,
            context,
            on_progress,
        )

        specialist_outputs = [
            market,
            competitor,
            funding,
            strategy,
        ]

        # ------------------------
        # Viability Score
        # ------------------------
        try:
            viability = self._score_viability(
                question,
                market,
                competitor,
                funding,
                strategy,
                on_progress,
            )
        except Exception:
            from types import SimpleNamespace

            viability = SimpleNamespace(
                overall_score=0,
                market_score=0,
                competition_score=0,
                funding_score=0,
                strategy_score=0,
            )

        # ------------------------
        # Final Report
        # ------------------------
        try:
            final_report = self._generate_report(
                question,
                context,
                specialist_outputs,
                on_progress,
            )
        except Exception:
            final_report = AgentOutput(
                content=f"""
    ```

    StartupIQ Report (Fallback)

    Question:
    {question}

    Context:
    {context[:1500]}
    """
    )


        return WorkflowResult(
            question=question,
            context=context,
            market=market,
            competitor=competitor,
            funding=funding,
            strategy=strategy,
            final_report=final_report,
            viability=viability,
            source_documents=source_documents,
        )

    def _retrieve_context(
        self,
        question: str,
        on_progress: ProgressCallback | None = None,
    ):
        _notify(on_progress, STEP_RAG, "running")

        try:
            result = self.rag.retrieve(question)

            if isinstance(result, tuple):
                context, documents = result
            else:
                documents = result
                context = "\n\n".join(
                    doc.page_content
                    for doc in documents
                    if hasattr(doc, "page_content")
                )

            _notify(on_progress, STEP_RAG, "complete")

            return context, documents

        except Exception:
            _notify(on_progress, STEP_RAG, "error")
            raise

    def _run_agent(
        self,
        step_id,
        agent,
        question,
        context,
        on_progress=None,
    ):
        _notify(on_progress, step_id, "running")

        try:
            output = agent.run(question, context)
            _notify(on_progress, step_id, "complete")
            return output

        except Exception:
            _notify(on_progress, step_id, "error")
            raise

    def _score_viability(
        self,
        question,
        market,
        competitor,
        funding,
        strategy,
        on_progress=None,
    ):
        _notify(on_progress, STEP_VIABILITY, "running")

        scorer = ViabilityScorer()

        result = scorer.score(
            question,
            market,
            competitor,
            funding,
            strategy,
        )

        _notify(on_progress, STEP_VIABILITY, "complete")

        return result

    def _generate_report(
        self,
        question,
        context,
        specialist_outputs,
        on_progress=None,
    ):
        _notify(on_progress, STEP_REPORT, "running")

        report_agent = ReportGeneratorAgent()

        report = report_agent.generate(
            question,
            context,
            specialist_outputs,
        )

        _notify(on_progress, STEP_REPORT, "complete")

        return report


def run_multi_agent_workflow(
    question: str,
    context: str,
    on_progress: ProgressCallback | None = None,
    ):
    orch = StartupIQOrchestrator()

    
    market = orch._run_agent(
        STEP_MARKET,
        MarketResearchAgent(),
        question,
        context,
        on_progress,
    )

    competitor = orch._run_agent(
        STEP_COMPETITOR,
        CompetitorAnalysisAgent(),
        question,
        context,
        on_progress,
    )

    funding = orch._run_agent(
        STEP_FUNDING,
        FundingAdvisorAgent(),
        question,
        context,
        on_progress,
    )

    strategy = orch._run_agent(
        STEP_STRATEGY,
        BusinessStrategyAgent(),
        question,
        context,
        on_progress,
    )

    specialists = [
        market,
        competitor,
        funding,
        strategy,
    ]

    report = orch._generate_report(
        question,
        context,
        specialists,
        on_progress,
    )

    return specialists, report
        

def _notify(callback, step_id, status):
    if callback:
        callback(step_id, status)
