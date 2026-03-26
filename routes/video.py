import os
import uuid
import tempfile
from typing import Dict, Set

import cv2
from fastapi import APIRouter, File, UploadFile, HTTPException
from ultralytics import YOLO

router = APIRouter(prefix="/video", tags=["video"])

# COCO vehicle class ids
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

model = YOLO("yolov8n.pt")


def get_lane_index(x_center: float, frame_width: int) -> int:
    lane_width = frame_width / 4
    lane = int(x_center // lane_width)
    return max(0, min(3, lane))


@router.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    suffix = os.path.splitext(file.filename)[1] or ".mp4"
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}{suffix}")

    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        cap = cv2.VideoCapture(temp_path)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Could not open video")

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # unique track ids per lane
        lane_track_ids: Dict[int, Set[int]] = {
            0: set(),
            1: set(),
            2: set(),
            3: set(),
        }

        # per class counting
        lane_class_counts = {
            0: {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0},
            1: {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0},
            2: {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0},
            3: {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0},
        }

        # track_id -> (lane, class_name) to avoid duplicate recount
        already_counted = set()

        processed_frames = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            processed_frames += 1

            # speed ke liye har 2nd frame process kar rahe hain
            if processed_frames % 2 != 0:
                continue

            results = model.track(
                frame,
                persist=True,
                verbose=False,
                conf=0.35,
                tracker="bytetrack.yaml",
            )

            if not results or results[0].boxes is None:
                continue

            boxes = results[0].boxes

            if boxes.id is None:
                continue

            ids = boxes.id.int().cpu().tolist()
            classes = boxes.cls.int().cpu().tolist()
            xyxy = boxes.xyxy.cpu().tolist()

            for track_id, cls_id, box in zip(ids, classes, xyxy):
                if cls_id not in VEHICLE_CLASSES:
                    continue

                x1, y1, x2, y2 = box
                x_center = (x1 + x2) / 2
                lane = get_lane_index(x_center, frame_width)
                class_name = VEHICLE_CLASSES[cls_id]

                unique_key = (track_id, lane, class_name)
                if unique_key in already_counted:
                    continue

                already_counted.add(unique_key)
                lane_track_ids[lane].add(track_id)
                lane_class_counts[lane][class_name] += 1

        cap.release()

        lane_counts = {
            "lane1": sum(lane_class_counts[0].values()),
            "lane2": sum(lane_class_counts[1].values()),
            "lane3": sum(lane_class_counts[2].values()),
            "lane4": sum(lane_class_counts[3].values()),
        }

        total_vehicles = sum(lane_counts.values())

        return {
            "success": True,
            "totalVehicles": total_vehicles,
            "laneCounts": lane_counts,
            "laneClassCounts": {
                "lane1": lane_class_counts[0],
                "lane2": lane_class_counts[1],
                "lane3": lane_class_counts[2],
                "lane4": lane_class_counts[3],
            },
            "processedFrames": processed_frames,
            "frameWidth": frame_width,
            "totalFrames": frame_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)