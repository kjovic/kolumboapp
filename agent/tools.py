from typing import Any, Callable, List
from typing_extensions import Annotated
from langgraph.prebuilt import InjectedState
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.tools import tool
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from apify_client import ApifyClient


@tool
def search_hotels_with_apify(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[dict, InjectedState],
):
    """Search hotels on Booking.com using Apify Booking Scraper based on user input."""

    client = ApifyClient("apify_api_NII4yuxkyarmhgvEwLsxXgIJAHjYbw3HyvbX")

    run_input = {
        "search": state["destination_location"],
        "checkIn": state["travel_dates"]["check_in"],
        "checkOut": state["travel_dates"]["check_out"],
        "rooms": state.get("rooms", 1),
        "adults": state.get("travelers", 2),
        "children": state.get("children", 0),
        "maxItems": 3,
        "propertyType": state.get("property_type", "Hotels"),
        "currency": state.get("currency", "EUR"),
        "language": state.get("desired_language", "en-gb"),
        "sortBy": state.get("sort_by", "bayesian_review_score"),
        "minMaxPrice": state.get("min_max_price", "0-99999"),
    }

    run = client.actor("voyager/booking-scraper").call(run_input=run_input)

    hotels = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        hotel_info = {
            "name": item.get("name"),
            "price": item.get("price"),
            "rating": item.get("reviewScore"),
            "location": item.get("location"),
            "booking_url": item.get("url"),  # Ovo vraća Apify direktno
        }
        hotels.append(hotel_info)

    return Command(
        update={
            "hotels": hotels,
            "messages": [
                ToolMessage(
                    f"Found {len(hotels)} hotels for {state['destination_location']}. "
                    f"Here are the top options you can book directly via the provided links.",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


@tool
def return_hotels(state: Annotated[dict, InjectedState]):
    """When users want to book something or after we found list of hotels we invoke this most important attribute is Booking link"""
    return state.get("hotels")


@tool
def set_booking_details(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[dict, InjectedState],
    destination_location: str = None,
    check_in: str = None,
    check_out: str = None,
    travelers: int = None,
    children: int = None,
    rooms: int = None,
    min_score: str = None,
    property_type: str = None,
    max_price: str = None,
):
    """Set booking search filters dynamically based on user input."""

    update_dict = {
        "destination_location": destination_location,
        "travel_dates": {"check_in": check_in, "check_out": check_out},
        "travelers": travelers,
        "children": children,
        "rooms": rooms,
        "min_score": min_score,
        "property_type": property_type,
        "max_price": max_price,
        "messages": [
            ToolMessage(
                f"Booking filters updated for {destination_location} from {check_in} to {check_out}",
                tool_call_id=tool_call_id,
            )
        ],
    }

    # Remove None values
    update_dict = {k: v for k, v in update_dict.items() if v is not None}

    return Command(update=update_dict)


@tool(parse_docstring=False)
def set_desired_language(
    tool_call_id: Annotated[str, InjectedToolCallId], language: str
):
    """Set desired language."""

    return Command(
        update={
            "desired_language": language,
            "messages": [
                ToolMessage(
                    f"Language set to {language}",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


@tool
def retrieve_desired_language(state: Annotated[dict, InjectedState]):
    """Retrieve desired language."""
    return state.get("desired_language")


BOOKING_AGENT_TOOLS: List[Callable[..., Any]] = [
    search_hotels_with_apify,
    set_booking_details,
    set_desired_language,
    retrieve_desired_language,
    return_hotels,
]
