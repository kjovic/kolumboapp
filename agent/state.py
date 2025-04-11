from typing import Optional, List, Dict
from pydantic import BaseModel
from langgraph.prebuilt.chat_agent_executor import AgentState


class Address(BaseModel):
    full: str
    postalCode: Optional[str]
    street: Optional[str]
    country: Optional[str]
    region: Optional[str]


class CategoryReview(BaseModel):
    title: str
    score: float


class Hotel(BaseModel):
    name: str
    description: Optional[str]
    address: Address
    stars: Optional[int]
    rating: Optional[float]
    reviews: Optional[int]
    categoryReviews: Optional[List[CategoryReview]]
    price: Optional[float]
    currency: Optional[str]
    checkIn: Optional[str]
    checkOut: Optional[str]
    image: Optional[str]  # Main image
    images: Optional[List[str]]  # All images
    booking_url: str


class State(AgentState):
    active_agent: Optional[str]
    desired_language: Optional[str]
    destination_location: Optional[str]
    hotels: Optional[List[Hotel]]  # Lista hotela
    selected_hotel: Optional[Hotel]  # Kada user izabere hotel
    travel_dates: Optional[Dict]  # {"check_in": "...", "check_out": "..."}
    travelers: Optional[int]
    children: Optional[int]
    rooms: Optional[int]
    min_score: Optional[str]
    property_type: Optional[str]
    max_price: Optional[str]
    user_query: Optional[str]
