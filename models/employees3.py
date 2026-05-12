from typing import Optional
from pydantic import BaseModel


class DateRange(BaseModel):
    start_date: str
    end_date: Optional[str] = None


class Job(BaseModel):
    job_id: str
    pay_type: str
    pay_value: float
    is_primary: bool
    job_periods: list[DateRange]


class LocationAssignment(BaseModel):
    location_id: str
    start_date: str
    end_date: Optional[str] = None


class Employee(BaseModel):
    employee_id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    employment_status: str
    employment_periods: list[DateRange]
    jobs: list[Job]
    locations: list[LocationAssignment]
    preferred_name: Optional[str] = None
