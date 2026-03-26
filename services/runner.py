import asyncio
import cv2

from services.detector import detect_vehicles
from services.traffic_engine import calculate_signal_times
from services.corridor import green_corridor
from websocket import manager

# 🎥 Webcam init
# cap = cv2.VideoCapture(0)
cap = None

def get_camera_frame():
    ret, frame = cap.read()
    if not ret:
        return None
    return frame


# 🚀 MAIN LOOP
async def traffic_loop():
    while True:
        try:
            # frame = get_camera_frame()
            frame = None

            # ❗ Agar frame nahi mila to skip
            if frame is None:
                await asyncio.sleep(1)
                continue

            # 🔍 AI Detection
            # result = detect_vehicles(frame)
            result = {
                "count": 0,
                "emergency": False
            }

            # 🚑 Emergency logic
            if result["emergency"]:
                signals = green_corridor([0, 1, 2])  # route lanes
            else:
                # 🚦 Normal AI traffic logic
                signals = calculate_signal_times([10, 20, 5, 15])

            # 📡 Frontend ko data bhejna
            await manager.broadcast({
                "signals": signals,
                "vehicles": result["count"],
                "emergency": result["emergency"]
            })

            # ⏱️ delay (important)
            await asyncio.sleep(1)

        except Exception as e:
            print("Error in loop:", e)
            await asyncio.sleep(1)