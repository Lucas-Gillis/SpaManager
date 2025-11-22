from . import appointments, auth, clients, public, staff
from .appointments import router as appointments_router
from .auth import router as auth_router
from .clients import router as clients_router
from .public import router as public_router
from .staff import router as staff_router

__all__ = [
    "appointments",
    "appointments_router",
    "auth",
    "auth_router",
    "clients",
    "clients_router",
    "public",
    "public_router",
    "staff",
    "staff_router",
]
