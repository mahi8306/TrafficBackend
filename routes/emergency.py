# routes/emergency.py
from fastapi import APIRouter
from services.corridor import green_corridor

router = APIRouter()

@router.post("/emergency")
def handle_emergency(data: dict):
    route = data["route"]  # [0,1,2]

    signals = green_corridor(route)

    return {
        "signals": signals
    }