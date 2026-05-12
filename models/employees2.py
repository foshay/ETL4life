from typing import Optional
from pydantic import BaseModel


class Job(BaseModel):
    job_id: str
    pay_type: str
    pay_value: float


class Employee(BaseModel):
    employee_id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    employment_status: str
    hire_date: str
    termination_date: Optional[str] = None
    job: Job
    location: str
    preferred_name: Optional[str] = None
