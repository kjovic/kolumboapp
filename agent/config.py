"""Agent configuration."""

from __future__ import annotations
from typing import Optional
from typing_extensions import Annotated, Literal
from dataclasses import dataclass, field, fields
from langchain_core.runnables import RunnableConfig, ensure_config


SYSTEM_PROMPT_HOTEL_AGENT = """
You are a Smart Hotel Booking Assistant.

# Behavior:
- Always start the conversation like:
"Hello! I am your Smart Hotel Booking Assistant. I can help you find the perfect hotel for your trip."

# Important Rules:
- Always use Apify Booking Scraper tool for hotel search.
- Show the top 4 hotels based on review score and relevance.
- Always display: hotel name, price, rating, and location.
- Be friendly, professional, and helpful.
- Never invent data.
"""


ModelChoice = Literal[
    "google_genai/gemini-2.0-flash",
    "google_genai/gemini-2.0-flash-lite",
    "google_genai/gemini-2.5-pro-exp-03-25",
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/o3-mini",
]


@dataclass(kw_only=True)
class Configuration:
    """Configuration for the Hotel Booking Agent."""

    use_custom_prompt: bool = field(
        default=False,
        metadata={
            "description": "Use a custom system prompt if True, otherwise default hotel agent prompt.",
            "json_schema_extra": {"langgraph_nodes": ["booking_agent"]},
        },
    )

    custom_system_prompt: Optional[str] = field(
        default=None,
        metadata={
            "description": "Custom system prompt text (used only if use_custom_prompt=True).",
            "json_schema_extra": {
                "langgraph_nodes": ["booking_agent"],
                "ui_hints": {"type": "textarea"},
            },
        },
    )

    model: Annotated[ModelChoice, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="openai/gpt-4o",
        metadata={
            "description": "Language model to use.",
            "json_schema_extra": {"langgraph_nodes": ["booking_agent"]},
        },
    )

    @property
    def system_prompt(self) -> str:
        """Return the active system prompt text."""
        if self.use_custom_prompt and self.custom_system_prompt:
            return self.custom_system_prompt
        return SYSTEM_PROMPT_HOTEL_AGENT

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create Configuration from RunnableConfig."""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})
