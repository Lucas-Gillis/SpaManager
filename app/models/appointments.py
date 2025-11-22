from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    completed = "completed"
    canceled = "canceled"


class Appointment(BaseModel):
    id: int
    client_id: int
    staff_member: str
    service: str
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus = AppointmentStatus.scheduled


class AppointmentCreate(BaseModel):
    client_id: int
    staff_member: str
    service: str
    start_time: datetime
    end_time: datetime
