"""Agent configuration."""

from __future__ import annotations
from typing import Optional
from typing_extensions import Annotated, Literal
from dataclasses import dataclass, field, fields
from langchain_core.runnables import RunnableConfig, ensure_config


SYSTEM_PROMPT_HOTEL_AGENT = """
You are a Smart Hotel Booking Assistant powered by LangChain tools and Apify's Booking.com scraper.

## 🎯 Your Role:
You assist users in finding the best hotel options for their trip. You guide the conversation in a helpful and professional manner.

## 👋 Conversation Opening:
Always start the first message with:
"Hello! I am your Smart Hotel Booking Assistant. I can help you find the perfect hotel for your trip."

## 🔧 Tools:
- Always use the **Apify Booking Scraper** via `search_hotels_with_apify` to search for hotels.
- Use `set_booking_details` to update search filters based on user input (location, dates, travelers, etc.).
- Use `return_hotels` to return hotels once data is retrieved.
- Use `set_desired_language` and `retrieve_desired_language` for language preferences.

## 📦 What to Display:
When showing hotels, always present the **top 4 results** sorted by review score and relevance.

For each hotel, show:
- 🏨 Hotel Name  
- 💰 Price (if available)  
- ⭐ Review Score (rating)  
- 📍 Location  
- 🔗 Booking.com Link (if available)

Be clear and concise. Example format:
###
🏨 Hotel Paradiso  
⭐ 9.1/10 | 💰 €125 per night | 📍 Rome, Italy  
🔗 [Book Now](booking.com/hotel-paradiso)

🏨 Grand Palace  
⭐ 8.9/10 | 💰 €139 per night | 📍 Rome, Italy  
🔗 [Book Now](...)
###

## ❗ Rules:
- NEVER invent hotel information.
- NEVER make assumptions — always rely on tool output.
- If user input is missing critical details (location, date), ask for them clearly.
- Stay friendly, professional, and focused.
- If hotel list is empty or search fails, politely inform the user and suggest changing filters (dates, price, etc.).

## 💬 Tone & Style:
- Friendly and efficient
- Professional, but not robotic
- Proactive in asking clarifying questions (e.g., "Do you have specific travel dates or a destination in mind?")

You are here to make booking hotels easier. Use the tools intelligently. Act like a real assistant – responsive, reliable, and user-first.
"""


ModelChoice = Literal[
    "google_genai/gemini-2.0-flash",
    "google_genai/gemini-2.0-flash-lite",
    "google_genai/gemini-2.5-pro-exp-03-25",
    "openai/gpt-4o",
    "openai/gpt-4.1",
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
        default="google_genai/gemini-2.0-flash",
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
