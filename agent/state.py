# agent/state.py (ili gdje god definiraš State)
from typing import Dict, List, Optional
from langgraph.prebuilt.chat_agent_executor import AgentState

# Importiraj modele koje si definirao (pretpostavimo da su u agent/models/booking.py i agent/models/flights.py)
from agent.models.booking import Hotel
from agent.models.flights import FlightData  # Importiraj FlightData model


class State(AgentState):
    # --- Existing Booking Fields ---
    active_agent: Optional[str]
    desired_language: Optional[str]
    destination_location: Optional[str]  # Može se koristiti i za letove
    hotels: Optional[List[Hotel]]
    selected_hotel: Optional[Hotel]
    travel_dates: Optional[
        Dict
    ]  # {"check_in": "...", "check_out": "..."} - Možda preimenovati u booking_dates?
    travelers: Optional[int]  # Može se koristiti i za letove
    children: Optional[int]  # Može se koristiti i za letove
    rooms: Optional[int]
    min_score: Optional[str]
    property_type: Optional[str]
    max_price: Optional[str]
    user_query: Optional[str]  # Dodajemo ovo za općeniti upit

    # --- New Flight Fields ---
    origin_location: Optional[str] = None  # Mjesto polaska leta
    # destination_location se može dijeliti, ali ako želiš odvojeno: flight_destination_location: Optional[str] = None
    departure_date: Optional[str] = None  # Datum polaska leta
    return_date: Optional[str] = None  # Datum povratka (opcionalno za round-trip)
    # travelers se može dijeliti, ali ako želiš odvojeno: flight_passengers: Optional[int] = None
    flights: Optional[List[FlightData]] = None  # Lista pronađenih letova
    selected_flight: Optional[FlightData] = None  # Kada user izabere let

    # Možda dodati i druge filtere za letove ako je potrebno (npr. direct_flights_only)
