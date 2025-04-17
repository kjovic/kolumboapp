from typing import Optional, List, Dict
from pydantic import BaseModel


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
