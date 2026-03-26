# # services/detector.py
# from ultralytics import YOLO

# model = YOLO("yolov8n.pt")

# def detect_vehicles(frame):
#     results = model(frame)

#     vehicles = []
#     emergency = False
   

#     for r in results:
#         for box in r.boxes:
#             cls = int(box.cls[0])

#             if cls in [2, 3, 5, 7]:  # car, bike, bus, truck
#                 vehicles.append(cls)

#             if cls == 1:  # assume ambulance class
#                 emergency = True

#     return {
#         "count": len(vehicles),
#         "emergency": emergency
#     }



# from ultralytics import YOLO

# model = YOLO("yolov8n.pt")

# def detect_vehicles(frame):
#     results = model(frame)

#     vehicles = []
#     boxes_data = []

#     for r in results:
#         for box in r.boxes:
#             cls = int(box.cls[0])
#             label = model.names[cls]

#             if label in ["car", "motorcycle", "bus", "truck"]:
#                 vehicles.append(label)

#                 x1, y1, x2, y2 = box.xyxy[0].tolist()

#                 boxes_data.append({
#                     "x1": int(x1),
#                     "y1": int(y1),
#                     "x2": int(x2),
#                     "y2": int(y2),
#                     "label": label
#                 })

#     return {
#         "count": len(vehicles),
#         "boxes": boxes_data,
#         "emergency": False
#     }




# from ultralytics import YOLO

# model = YOLO("yolov8s.pt")

# def detect_vehicles(frame):
#     results = model(frame)

#     vehicles = []
#     boxes_data = []

#     for r in results:
#         for box in r.boxes:
#             cls = int(box.cls[0])
#             conf = float(box.conf[0])
#             label = model.names[cls]

#             print("Detected:", label, "Conf:", round(conf, 2))

#             x1, y1, x2, y2 = box.xyxy[0].tolist()

#             boxes_data.append({
#                 "x1": int(x1),
#                 "y1": int(y1),
#                 "x2": int(x2),
#                 "y2": int(y2),
#                 "label": label,
#                 "confidence": round(conf, 2)
#             })

#             # count only vehicles
#             if label in ["car", "motorcycle", "bus", "truck", "bicycle"]:
#                 vehicles.append(label)

#     return {
#         "count": len(vehicles),
#         "boxes": boxes_data,
#         "emergency": False
#     }



from ultralytics import YOLO

model = None
VEHICLE_LABELS = {"car", "motorcycle", "bus", "truck", "bicycle"}

try:
    model = YOLO("yolov8s.pt")
    print("YOLO loaded successfully")
except Exception as e:
    print("YOLO load failed:", e)

def detect_vehicles(frame):
    if model is None:
        return {"count": 0, "boxes": [], "error": "Model not loaded"}

    try:
        results = model.predict(frame, conf=0.4, imgsz=416, verbose=False)

        vehicles = []
        boxes_data = []

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = model.names[cls]

                if label not in VEHICLE_LABELS:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                boxes_data.append({
                    "x1": int(x1),
                    "y1": int(y1),
                    "x2": int(x2),
                    "y2": int(y2),
                    "label": label,
                    "confidence": round(conf, 2)
                })

                vehicles.append(label)

        return {"count": len(vehicles), "boxes": boxes_data, "emergency": False}

    except Exception as e:
        print("Detection error:", e)
        return {"count": 0, "boxes": [], "error": str(e)}