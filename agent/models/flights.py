# agent/models/flights.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field


class ParentPlace(BaseModel):
    """Simplified structure for the 'parent' field within FlightPlace."""

    flightPlaceId: Optional[str] = None
    displayCode: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None


class FlightPlace(BaseModel):
    """Represents an origin or destination within a segment."""

    flightPlaceId: Optional[str] = None
    displayCode: Optional[str] = None
    parent: Optional[ParentPlace] = None
    name: Optional[str] = None
    type: Optional[str] = None
    country: Optional[str] = None


class CarrierBase(BaseModel):
    """Base carrier info common to different contexts."""

    id: Optional[int] = None
    name: Optional[str] = None
    alternateId: Optional[str] = None
    logoUrl: Optional[HttpUrl] = None


class SegmentCarrier(CarrierBase):
    """Carrier info as found within segments (includes allianceId, displayCode)."""

    allianceId: Optional[int] = None
    displayCode: Optional[str] = None


class LegCarrier(CarrierBase):
    """Carrier info as found within legs.carriers (might lack allianceId/displayCode)."""

    pass


class Segment(BaseModel):
    id: Optional[str] = None
    origin: Optional[FlightPlace] = None
    destination: Optional[FlightPlace] = None
    departure: Optional[str] = None
    arrival: Optional[str] = None
    durationInMinutes: Optional[int] = None
    flightNumber: Optional[str] = None
    marketingCarrier: Optional[SegmentCarrier] = None
    operatingCarrier: Optional[SegmentCarrier] = None
    transportType: Optional[str] = None


class LegLocation(BaseModel):
    """Represents an origin or destination at the Leg level."""

    id: Optional[str] = None
    entityId: Optional[str] = None
    name: Optional[str] = None
    displayCode: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    isHighlighted: Optional[bool] = None


class LegCarriers(BaseModel):
    """Structure for carriers within a Leg."""

    marketing: Optional[List[LegCarrier]] = None
    operating: Optional[List[LegCarrier]] = None
    operationType: Optional[str] = None


class Leg(BaseModel):
    id: Optional[str] = None
    origin: Optional[LegLocation] = None
    destination: Optional[LegLocation] = None
    durationInMinutes: Optional[int] = None
    stopCount: Optional[int] = None
    isSmallestStops: Optional[bool] = None
    departure: Optional[str] = None
    arrival: Optional[str] = None
    timeDeltaInDays: Optional[int] = None
    carriers: Optional[LegCarriers] = None
    segments: Optional[List[Segment]] = None


class Price(BaseModel):
    raw: Optional[float] = None
    formatted: Optional[str] = None
    pricingOptionId: Optional[str] = None


class Eco(BaseModel):
    ecoContenderDelta: Optional[float] = None


class FarePolicy(BaseModel):
    isChangeAllowed: Optional[bool] = None
    isPartiallyChangeable: Optional[bool] = None
    isCancellationAllowed: Optional[bool] = None
    isPartiallyRefundable: Optional[bool] = None


class PriceDetail(BaseModel):
    updateStatus: Optional[str] = None
    amount: Optional[float] = None


class SegmentIdItem(BaseModel):
    price: Optional[PriceDetail] = None
    segmentIds: Optional[List[str]] = None
    bookingProposition: Optional[str] = None
    agentId: Optional[str] = None
    url: Optional[HttpUrl] = None


class PricingOption(BaseModel):
    agentIds: Optional[List[str]] = None
    price: Optional[PriceDetail] = None
    items: Optional[List[SegmentIdItem]] = None
    pricingOptionId: Optional[str] = None
    fareAttributes: Optional[Dict[str, Any]] = Field(default_factory=dict)
    agentNames: Optional[List[str]] = None
    agentName: Optional[str] = None


class FlightData(BaseModel):
    price: Optional[Price] = None
    vendor: Optional[str] = None
    firstCarrier: Optional[str] = None
    url: Optional[HttpUrl] = None
    eco: Optional[Eco] = None
    fareAttributes: Optional[Dict[str, Any]] = Field(default_factory=dict)
    farePolicy: Optional[FarePolicy] = None
    hasFlexibleOptions: Optional[bool] = None
    id: Optional[str] = None
    isMashUp: Optional[bool] = None
    isProtectedSelfTransfer: Optional[bool] = None
    isSelfTransfer: Optional[bool] = None
    legs: Optional[List[Leg]] = None
    pricingOptions: Optional[List[PricingOption]] = None
    score: Optional[float] = None
    tags: Optional[List[str]] = None


class Root(BaseModel):
    data: Optional[List[FlightData]] = None
