from typing import Optional
from pydantic import BaseModel

class Location(BaseModel):
    location_id: int
    name: str
    address: str
    open_date: str