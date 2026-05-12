from typing import Optional
from pydantic import BaseModel


class Employee(BaseModel):
    employee_id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    hire_date: str
    job_id: str
    pay_type: str
    salary: Optional[float] = None
    hourly_rate: Optional[float] = None
    location: str
    preferred_name: Optional[str] = None
