from fastapi import FastAPI

from .core.auth import AuthMiddleware
from .core.config import get_settings
from .routes import appointments, auth, clients, public, staff



def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Backend API for managing spa operations."
    )

    app.add_middleware(AuthMiddleware)

    app.include_router(public.router)
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
    app.include_router(clients.router, prefix="/clients", tags=["clients"])
    app.include_router(staff.router, prefix="/staff", tags=["staff"])

    return app
