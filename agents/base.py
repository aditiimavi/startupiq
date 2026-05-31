"""Base agent: shared LLM setup and analysis interface."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


@dataclass
class AgentOutput:
    """Structured result from a single specialist agent."""
    agent_name: str
    content: str


class BaseAgent:
    """
    Abstract specialist agent.
    """

    agent_name = "Base Agent"
    system_prompt = "You are a helpful startup analyst."

    def __init__(self) -> None:

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. Add it to your .env file."
            )

        self.llm = ChatGroq(
            api_key=api_key,
            model_name="llama-3.1-8b-instant",
            temperature=0.3,
        )

    def _build_prompt(self, question: str, context: str) -> str:

        return f"""
SYSTEM:
{self.system_prompt}

USER QUESTION:
{question}

DOCUMENT CONTEXT:
{context}
"""

    def analyze(self, question: str, context: str) -> AgentOutput:

        prompt = self._build_prompt(question, context)

        try:
            response = self.llm.invoke(prompt)

            text = (
                response.content
                if hasattr(response, "content")
                else str(response)
            )

            return AgentOutput(
                agent_name=self.agent_name,
                content=text.strip(),
            )

        except Exception as e:
            return AgentOutput(
                agent_name=self.agent_name,
                content=f"Agent execution failed: {str(e)}",
            )