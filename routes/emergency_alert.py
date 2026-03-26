# from fastapi import APIRouter
# from pydantic import BaseModel
# from datetime import datetime

# router = APIRouter(prefix="/emergency", tags=["Emergency"])

# class EmergencyRequest(BaseModel):
#     sender: str
#     latitude: float
#     longitude: float

# @router.post("/alert")
# async def emergency_alert(data: EmergencyRequest):
#     return {
#         "success": True,
#         "message": "Emergency alert received",
#         "sender": data.sender,
#         "coordinates": {
#             "latitude": data.latitude,
#             "longitude": data.longitude
#         },
#         "timestamp": datetime.utcnow().isoformat()
#     }




from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/emergency", tags=["Emergency"])

# 🔥 GLOBAL STORAGE (important)
latest_emergency_alert = None


class EmergencyRequest(BaseModel):
    sender: str
    latitude: float
    longitude: float


# 🚨 SEND ALERT
@router.post("/alert")
async def emergency_alert(data: EmergencyRequest):
    global latest_emergency_alert

    latest_emergency_alert = {
        "id": str(uuid.uuid4()),
        "active": True,
        "sender": data.sender,
        "coordinates": {
            "latitude": data.latitude,
            "longitude": data.longitude
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    return {
        "success": True,
        "message": "Emergency alert received",
        "alert": latest_emergency_alert
    }


# 📡 GET LATEST ALERT (polling ke liye)
@router.get("/latest")
async def get_latest_emergency():
    if latest_emergency_alert is None:
        return {"active": False}
    return latest_emergency_alert


# ❌ CLEAR ALERT
@router.post("/clear")
async def clear_emergency():
    global latest_emergency_alert
    latest_emergency_alert = None
    return {"success": True}