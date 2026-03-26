# routes/traffic.py
from fastapi import APIRouter
from services.traffic_engine import calculate_signal_times

router = APIRouter()

@router.post("/traffic/update")
def update_traffic(data: dict):
    lanes = data["lanes"]  # [10,20,5,15]

    timings = calculate_signal_times(lanes)

    return {
        "timings": timings
    }