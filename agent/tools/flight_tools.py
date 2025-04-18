# agent/tools/flight_tools.py
import json
import os
from typing import Any, Callable, List, Optional
from typing_extensions import Annotated
from langgraph.prebuilt import InjectedState
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.tools import tool
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from apify_client import ApifyClient
from pydantic import ValidationError
from datetime import datetime
from agent.models.flights import FlightData

APIFY_API_KEY = os.getenv("APIFY_API_KEY")


def format_date_yyyymmdd_to_yymmdd(date_str: Optional[str]) -> Optional[str]:
    """Converts YYYY-MM-DD to YYMMDD if possible."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%y%m%d")
    except ValueError:
        print(f"Warning: Could not parse date {date_str}. Expected YYYY-MM-DD format.")
        return None  # Vrati None ako format nije dobar


@tool
def search_flights_with_apify(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[dict, InjectedState],
):
    """Search flights using Apify Skyscanner Scraper (wIfblEie7OF0dOs3C) based on current state."""

    # --- 1. Get data from state ---
    origin = state.get("origin_location")
    destination = state.get("destination_location")
    depart_date_str = state.get("departure_date")
    return_date_str = state.get("return_date")  # Može biti None
    passengers = state.get("travelers", 1)
    children_count = state.get("children", 0)  # Trenutno samo broj djece

    # --- 2. Validate required data ---
    if not all([origin, destination, depart_date_str]):
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        "Missing required flight details: origin, destination, or departure date.",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    if not APIFY_API_KEY:  # Jednostavnija provjera
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        "Apify API key is not configured. Cannot search flights.",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    # --- 3. Format data for Apify Actor ---
    depart_date_formatted = format_date_yyyymmdd_to_yymmdd(depart_date_str)
    return_date_formatted = format_date_yyyymmdd_to_yymmdd(
        return_date_str
    )  # Vratit će None ako return_date_str nije postavljen

    if not depart_date_formatted:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        f"Invalid departure date format: {depart_date_str}. Expected YYYY-MM-DD.",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )
    # Nije nužno greška ako return date nije dobar format, možda je one-way
    # if return_date_str and not return_date_formatted:
    #      # Handle error or proceed with one-way?

    client = ApifyClient(APIFY_API_KEY)
    actor_id = "wIfblEie7OF0dOs3C"

    # --- 4. Construct run_input based on Apify example ---
    run_input = {
        "origin": origin,
        "destination": destination,
        "datefrom": depart_date_formatted,  # Koristi formatirani datum
        # "dateto": return_date_formatted, # Dodaj samo ako postoji
        "adults": passengers,
        # "children": [], # PROBLEM: Treba lista godina. Za sada šaljemo praznu listu ili izostavljamo.
        # Ako actor zahtijeva, ovo će možda uzrokovati grešku.
        # Idealno bi bilo prilagoditi state i set_flight_details.
        "market": "Hrvatska",  # Ispravljeno prema primjeru, idealno dinamički
        "direct": True,  # Dodano prema primjeru, idealno dinamički
        "classtype": "economy",  # Dodano prema primjeru, idealno dinamički
        "currency": "EUR",
        "locale": state.get("desired_language", "en-GB"),
        "maxItems": 5,  # Ograniči broj rezultata za testiranje/brzinu
        # --- Opcionalni parametri iz primjera koje možemo dodati ako treba ---
        # "format": True,
        # "process": "gfp",
        # "proxy": { "useApifyProxy": True, "apifyProxyGroups": [] },
        # "nearby": "none",
        # "delay": 3,
        # "retries": 3
    }

    # Dodaj povratni datum samo ako postoji i formatiran je
    if return_date_formatted:
        run_input["dateto"] = return_date_formatted

    # Opcionalno: Dodaj djecu ako je potrebno (ali format je problematičan)
    # if children_count > 0:
    #    run_input["children"] = [] # Ili [1] * children_count kao placeholder? Provjeriti actor!

    print(f"--- Calling Apify Actor '{actor_id}' with input: ---")
    print(json.dumps(run_input, indent=2))  # Koristi json.dumps za ljepši ispis
    print("----------------------------------------------------")

    # --- 5. Call Apify Actor and Process Results ---
    try:
        run = client.actor(actor_id).call(run_input=run_input)
        print(f"--- Apify Run Info ---")
        print(run)
        print("----------------------")

        flights_list = []
        dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            "Apify actor run did not return a dataset ID.",
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

        print(f"Fetching items from dataset: {dataset_id}")
        # Ispravljeno parsiranje prema primjeru outputa: item -> item['data'] -> iteracija
        dataset_items = list(
            client.dataset(dataset_id).iterate_items()
        )  # Dohvati sve iteme odjednom

        if not dataset_items:
            print("Warning: Apify dataset is empty.")
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            f"No data returned from Apify for the search.",
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

        # Pretpostavka: Dataset sadrži jedan item s 'data' listom unutra
        # Ako može biti više itema, treba prilagoditi logiku
        for item in dataset_items:
            if (
                isinstance(item, dict)
                and "data" in item
                and isinstance(item["data"], list)
            ):
                print(
                    f"Found 'data' key with {len(item['data'])} potential flights in dataset item."
                )
                for flight_data_dict in item["data"]:
                    try:
                        # Parsiraj svaki rječnik iz 'data' liste kao FlightData
                        flight_obj = FlightData(**flight_data_dict)
                        flights_list.append(flight_obj)
                    except ValidationError as e:
                        print(f"Pydantic Validation Error parsing flight item: {e}")
                        # Logiraj rječnik koji uzrokuje grešku
                        # print(f"Failed item structure: {json.dumps(flight_data_dict, indent=2)}")
                    except Exception as e:
                        print(f"Error processing flight item dictionary: {e}")
            else:
                print(
                    f"Warning: Dataset item does not have the expected structure (missing 'data' list): {item}"
                )

        if not flights_list:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            f"No valid flight data could be parsed from the Apify dataset for {origin} to {destination}.",
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

        # --- 6. Return Success ---
        return Command(
            update={
                "flights": flights_list,
                "messages": [
                    ToolMessage(
                        f"Found {len(flights_list)} flight options for {origin} to {destination}. "
                        f"Details available.",
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    # --- 7. Handle Errors ---
    except Exception as e:
        # Uhvati specifičnije Apify greške ako je moguće
        print(f"Error calling Apify or processing results: {e}")
        import traceback

        traceback.print_exc()  # Ispiši cijeli traceback za debugiranje
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        f"An error occurred while searching for flights: {e}",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )


# Ostali alati (set_flight_details, return_flights) ostaju isti kao u prethodnom odgovoru
# ... (zalijepi kod za set_flight_details i return_flights ovdje) ...


@tool
def set_flight_details(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[dict, InjectedState],
    origin_location: Optional[str] = None,
    destination_location: Optional[str] = None,
    departure_date: Optional[str] = None,
    return_date: Optional[str] = None,
    travelers: Optional[int] = None,  # Koristimo postojeći 'travelers'
    children: Optional[int] = None,  # Koristimo postojeći 'children'
    # TODO: Dodati parametre za direct, classtype, market, children_ages ako želimo dinamičko postavljanje
):
    """Set flight search parameters based on user input. Dates should be in YYYY-MM-DD format."""

    update_dict = {}
    confirmation_parts = []

    if origin_location:
        update_dict["origin_location"] = origin_location
        confirmation_parts.append(f"origin {origin_location}")
    if destination_location:
        update_dict["destination_location"] = destination_location
        confirmation_parts.append(f"destination {destination_location}")
    if departure_date:
        # TODO: Možda dodati validaciju formata YYYY-MM-DD ovdje?
        update_dict["departure_date"] = departure_date
        confirmation_parts.append(f"departing {departure_date}")
    if return_date:
        # TODO: Možda dodati validaciju formata YYYY-MM-DD ovdje?
        update_dict["return_date"] = return_date
        confirmation_parts.append(f"returning {return_date}")
    if travelers:
        update_dict["travelers"] = travelers
        confirmation_parts.append(f"{travelers} travelers")
    if children is not None:
        update_dict["children"] = children
        if children > 0:
            confirmation_parts.append(f"with {children} children")

    if not confirmation_parts:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        "No flight details provided to set.", tool_call_id=tool_call_id
                    )
                ]
            }
        )

    confirmation_message = (
        "Flight details updated: " + ", ".join(confirmation_parts) + "."
    )
    update_dict["messages"] = [
        ToolMessage(confirmation_message, tool_call_id=tool_call_id)
    ]

    return Command(update=update_dict)


@tool
def return_flights(state: Annotated[dict, InjectedState]):
    """Returns the list of flights found in the previous search."""
    flights = state.get("flights")
    if not flights:
        return "No flights have been searched for or found yet."

    flight_summaries = []
    for i, flight in enumerate(flights):
        # Provjeri je li flight stvarno FlightData objekt
        if not isinstance(flight, FlightData):
            print(
                f"Warning: Item in state['flights'] is not a FlightData object: {type(flight)}"
            )
            continue

        summary = f"Option {i+1}: "
        if flight.price and flight.price.formatted:
            summary += f"Price: {flight.price.formatted}, "
        if flight.firstCarrier:
            summary += f"Main Carrier: {flight.firstCarrier}, "
        if flight.legs:
            try:  # Dodaj try-except za siguran pristup atributima
                outbound_leg = flight.legs[0]
                dep_time = (
                    outbound_leg.departure[:16] if outbound_leg.departure else "N/A"
                )
                arr_time = outbound_leg.arrival[:16] if outbound_leg.arrival else "N/A"
                origin_code = (
                    outbound_leg.origin.displayCode if outbound_leg.origin else "N/A"
                )
                dest_code = (
                    outbound_leg.destination.displayCode
                    if outbound_leg.destination
                    else "N/A"
                )
                duration = (
                    outbound_leg.durationInMinutes
                    if outbound_leg.durationInMinutes is not None
                    else "N/A"
                )
                stops = (
                    outbound_leg.stopCount
                    if outbound_leg.stopCount is not None
                    else "N/A"
                )

                summary += f"Outbound: {origin_code} {dep_time} -> {dest_code} {arr_time} ({duration} min"
                if stops != "N/A" and stops > 0:
                    summary += f", {stops} stop(s)"
                summary += "). "

                if len(flight.legs) > 1:
                    inbound_leg = flight.legs[1]
                    dep_time_ret = (
                        inbound_leg.departure[:16] if inbound_leg.departure else "N/A"
                    )
                    arr_time_ret = (
                        inbound_leg.arrival[:16] if inbound_leg.arrival else "N/A"
                    )
                    origin_code_ret = (
                        inbound_leg.origin.displayCode if inbound_leg.origin else "N/A"
                    )
                    dest_code_ret = (
                        inbound_leg.destination.displayCode
                        if inbound_leg.destination
                        else "N/A"
                    )
                    duration_ret = (
                        inbound_leg.durationInMinutes
                        if inbound_leg.durationInMinutes is not None
                        else "N/A"
                    )
                    stops_ret = (
                        inbound_leg.stopCount
                        if inbound_leg.stopCount is not None
                        else "N/A"
                    )

                    summary += f"Return: {origin_code_ret} {dep_time_ret} -> {dest_code_ret} {arr_time_ret} ({duration_ret} min"
                    if stops_ret != "N/A" and stops_ret > 0:
                        summary += f", {stops_ret} stop(s)"
                    summary += ")."
            except (AttributeError, IndexError, TypeError) as e:
                print(f"Error summarizing leg data for flight {i+1}: {e}")
                summary += "[Error summarizing leg details]. "

        # Linkovi
        link_found = False
        if flight.url:
            summary += f" Link: {flight.url}"
            link_found = True
        elif flight.pricingOptions:
            try:
                first_option = flight.pricingOptions[0]
                if first_option.items:
                    first_item = first_option.items[0]
                    if first_item.url:
                        summary += f" Link: {first_item.url}"
                        link_found = True
            except (AttributeError, IndexError, TypeError) as e:
                print(f"Error accessing pricing option URL for flight {i+1}: {e}")

        if not link_found:
            summary += " (No direct link found)"

        flight_summaries.append(summary.strip())  # Ukloni eventualni razmak na kraju

    return (
        "\n".join(flight_summaries)
        if flight_summaries
        else "No flight details could be summarized."
    )
