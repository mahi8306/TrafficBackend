from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from routes import traffic, emergency, video
from services.runner import traffic_loop
from websocket import manager
import asyncio

# added by me now
import base64
import cv2
import numpy as np
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.detector import detect_vehicles

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(traffic.router)
app.include_router(emergency.router)
app.include_router(video.router)
app.include_router(video.router)

class ImageData(BaseModel):
    image: str

@app.post("/detect")
async def detect(data: ImageData):
    image_data = data.image.split(",")[1]
    img_bytes = base64.b64decode(image_data)

    np_arr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    result = detect_vehicles(frame)

    return result

# Startup
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(traffic_loop())

# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)

# Root test
@app.get("/")
def root():
    return {"msg": "Traffic AI Backend Running"}