from dataclasses import dataclass

@dataclass(frozen=True)
class EmptyChargingStationsDTO:
    """DTO representing a search result with no charging stations found."""
    message: str = "No stations found in this area."
