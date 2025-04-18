from typing import Any, Callable, List

from agent.tools.booking_tools import (
    retrieve_desired_language,
    return_hotels,
    search_hotels_with_apify,
    set_booking_details,
    set_desired_language,
)
from agent.tools.flight_tools import (
    return_flights,
    search_flights_with_apify,
    set_flight_details,
)


AGENT_TOOLS: List[Callable[..., Any]] = [
    search_hotels_with_apify,
    set_booking_details,
    set_desired_language,
    retrieve_desired_language,
    return_hotels,
    set_flight_details,
    search_flights_with_apify,
    return_flights,
]
