# Cricket DRS Overlay API

This Flask-based API provides two main endpoints for processing cricket videos and JSON data through a multi-module pipeline and returning the final overlaid video.

## Endpoints

### `POST /api/process`

* **Description:** Accepts raw JSON data, runs it through enabled tracking and analysis modules, merges results, applies overlays, and returns the final video file.
* **Request Body:** JSON payload representing precomputed frames or analysis data (see **Accepted JSON Format** below).
* **Response:** `video/mp4` file attachment of the processed video.

### `POST /api/convert-video`

* **Description:** Accepts a local video file path, converts frames to JSON, processes through the same pipeline as `/api/process`, and returns the overlaid video.
* **Request Body:** JSON object with a single field:

  ```json
  {
    "video_path": "path/to/input_cricket_video.mp4"
  }
  ```
* **Response:** `video/mp4` file attachment of the processed video.

## Accepted JSON Format

When sending JSON directly to `/api/process`, the API expects an array of frame objects, each containing:

* `frame_id` (integer): Sequential identifier for the frame.
* `timestamp` (string): Timecode in `HH:MM:SS.mmm` format.
* `image_data` (string): Base64‑encoded JPEG image data of the frame.
* `metadata` (object): Additional info, e.g.:

  ```json
  {
    "camera_id": "cam_1"
  }
  ```

### Example JSON Payload (As required by Ball and Object Tracking Group)

```json
[
  {
    "frame_id": 1,
    "timestamp": "00:00:00.000",
    "image_data": "/9j/4AAQSkZJRgABA...",  
    "metadata": { "camera_id": "cam_1" }
  },
  {
    "frame_id": 2,
    "timestamp": "00:00:00.040",
    "image_data": "/9j/4AAQSkZJRgABA...",  
    "metadata": { "camera_id": "cam_1" }
  }
]
```

All endpoints respond with standard HTTP status codes and return error details in JSON when failures occur.
