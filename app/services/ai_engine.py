"""Central AI brain supporting optional OpenAI API and deterministic fallbacks."""
from __future__ import annotations

import os
from dataclasses import dataclass

PROMPT_TEMPLATES = {
    "hr": "You are an HR automation assistant. Task: {task}",
    "analyst": "You are a data analyst assistant. Task: {task}",
    "support": "You are a customer support assistant. Task: {task}",
    "admin": "You are an administrative assistant. Task: {task}",
    "sales": "You are a sales manager assistant. Task: {task}",
}


@dataclass
class AIEngine:
    api_key: str | None = None

    def __post_init__(self) -> None:
        if self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")

    def _mock_response(self, department: str, task: str) -> str:
        prefix = department.upper()
        return (
            f"[{prefix} AI MOCK] Processed request: '{task}'. "
            "Recommendation: prioritize high-impact actions, automate repetitive workflows, "
            "and track KPI movement weekly."
        )

    def process(self, department: str, task: str) -> str:
        """Return a response from OpenAI if available, otherwise deterministic mock output."""
        template = PROMPT_TEMPLATES.get(department, "General task: {task}")
        prompt = template.format(task=task)

        if not self.api_key:
            return self._mock_response(department, task)

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are AI Office Manager."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            return completion.choices[0].message.content or self._mock_response(department, task)
        except Exception:
            return self._mock_response(department, task)
