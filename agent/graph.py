from typing import Dict, List, Literal, cast
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models import BaseChatModel
from langchain.chat_models import init_chat_model
from agent.utils.config import Configuration
from agent.state import State
from langgraph.graph import StateGraph
from langgraph.constants import START
from langgraph.prebuilt import ToolNode

from agent.tools.tools import AGENT_TOOLS


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name like 'provider/model'."""
    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(model, model_provider=provider)


async def booking_agent(
    state: State,
    config: RunnableConfig,
) -> Dict[str, List[AIMessage]]:
    """Booking Agent which helps users find hotels using Apify Booking Scraper."""

    configuration = Configuration.from_runnable_config(config)

    model = load_chat_model(configuration.model).bind_tools(AGENT_TOOLS)

    response = cast(
        AIMessage,
        await model.ainvoke(
            [
                {"role": "system", "content": configuration.system_prompt},
                *state["messages"],
            ],
            config,
        ),
    )

    if state["is_last_step"] and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    return {"messages": [response]}


def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """Determine next step based on model output."""
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(f"Expected AIMessage, got {type(last_message).__name__}")
    return "tools" if last_message.tool_calls else "__end__"


builder = StateGraph(State, config_schema=Configuration)

builder.add_node("booking_agent", booking_agent)
builder.add_node("tools", ToolNode(AGENT_TOOLS))

builder.add_edge(START, "booking_agent")
builder.add_conditional_edges("booking_agent", route_model_output)
builder.add_edge("tools", "booking_agent")

graph = builder.compile()
graph.name = "booking-agent"
