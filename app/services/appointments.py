from __future__ import annotations

from datetime import datetime, timedelta
from itertools import count
from typing import Dict, Iterable, Optional

from ..models.appointments import Appointment, AppointmentCreate, AppointmentStatus



class InMemoryAppointmentService:
    def __init__(self):
        now = datetime.now()
        self._sequence = count(1)
        self._appointments: Dict[int, Appointment] = {
            1: Appointment(
                id=1,
                client_id=1,
                staff_member="Sara Staff",
                service="Deep Tissue Massage",
                start_time=now + timedelta(hours=2),
                end_time=now + timedelta(hours=3),
                status=AppointmentStatus.scheduled,
            ),
            2: Appointment(
                id=2,
                client_id=2,
                staff_member="Mark Manager",
                service="Facial Treatment",
                start_time=now - timedelta(days=1),
                end_time=now - timedelta(days=1, hours=-1),
                status=AppointmentStatus.completed,
            ),
        }
        self._sequence = count(len(self._appointments) + 1)

    def list_appointments(self) -> Iterable[Appointment]:
        return sorted(self._appointments.values(), key=lambda appt: appt.start_time)

    def list_client_appointments(self, client_id: int) -> Iterable[Appointment]:
        return sorted(
            (appt for appt in self._appointments.values() if appt.client_id == client_id),
            key=lambda appt: appt.start_time,
        )

    def create_appointment(self, request: AppointmentCreate) -> Appointment:
        identifier = next(self._sequence)
        appointment = Appointment(id=identifier, status=AppointmentStatus.scheduled, **request.model_dump())
        self._appointments[identifier] = appointment
        return appointment

    def update_status(self, appointment_id: int, status: AppointmentStatus) -> Optional[Appointment]:
        appointment = self._appointments.get(appointment_id)
        if not appointment:
            return None
        updated = appointment.model_copy(update={"status": status})
        self._appointments[appointment_id] = updated
        return updated
