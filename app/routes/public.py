from datetime import datetime

from fastapi import APIRouter

from app.core.auth import auth_config

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/health")
@auth_config(required=False)
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.get("/services")
@auth_config(required=False)
async def list_services():
    return [
        {"name": "Signature Facial", "duration_minutes": 60, "price": 140},
        {"name": "Hot Stone Massage", "duration_minutes": 90, "price": 180},
        {"name": "Body Scrub", "duration_minutes": 45, "price": 95},
    ]
