from typing import Optional
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str

class OperatingDates(BaseModel):
    open_date: str
    close_date: Optional[str]

class Location(BaseModel):
    location_id: int
    name: str
    address: Address
    operating_dates: OperatingDates