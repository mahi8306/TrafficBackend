from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/emergency", tags=["Emergency"])

class EmergencyRequest(BaseModel):
    sender: str
    latitude: float
    longitude: float

@router.post("/alert")
async def emergency_alert(data: EmergencyRequest):
    return {
        "success": True,
        "message": "Emergency alert received",
        "sender": data.sender,
        "coordinates": {
            "latitude": data.latitude,
            "longitude": data.longitude
        },
        "timestamp": datetime.utcnow().isoformat()
    }