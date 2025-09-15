# Ball and Object Tracking - JSON Base64 Data Reader

This module provides tools to read, decode, and process base64-encoded JSON data suitable for ball and object tracking in sports (e.g., cricket tracking with YOLOv8).

---

## Features

- Load base64-encoded images from a JSON file
- Decode images and visualize or save them
- Extract frame metadata like timestamps and IDs
- Integrate easily with object detection models (e.g., YOLOv8)
- Export detection results in structured JSON format

---

## JSON Data Format

The input JSON file should be a list of objects, where each object represents a frame:

```json
[
  {
    "frame_id": 1,
    "timestamp": "00:00:01.001",
    "image_data": "iVBORw0KGgoAAAANSUhEUgAA...",  // base64-encoded image
    "metadata": {
      "camera_id": "cam_1"
    }
  },
  ...
]



Usage:
import json
from utils import decode_base64_image

with open('data/sample.json', 'r') as f:
    data = json.load(f)

for frame in data:
    img = decode_base64_image(frame['image_data'])
    # Display or save the image


dependencies:
import base64
import numpy as np
import cv2

def decode_base64_image(base64_string):
    img_bytes = base64.b64decode(base64_string)
    np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img


YoloV8 integration:
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
results = model(img)

for result in results:
    for box in result.boxes:
        cls = result.names[int(box.cls[0])]
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        print(f"Detected {cls} at ({x1}, {y1}) - ({x2}, {y2})")


export data to json:
output_data = []

for frame in data:
    output_data.append({
        "frame_id": frame["frame_id"],
        "timestamp": frame["timestamp"],
        "detections": [
            {"label": cls, "bbox": [x1, y1, x2, y2]}
        ]
    })

with open("output/detections.json", "w") as f:
    json.dump(output_data, f, indent=2)
