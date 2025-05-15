# Group Members

- Mujtaba Ahmed
- Ahmad Abdul Rehman
- Hassaan Raza
- Burhan Bhatti
- Ibrahim Sohail
- M.Fahad

# Stream Analysis and Display Module

Processes trajectory data from ball tracking inputs to render real-time overlays for cricket Decision Review System (DRS).

## Features

- Real-time ball trajectory visualization
- Distinct rendering for actual and predicted paths
- Decision indicators (OUT/NOT OUT) with confidence metrics
- Support for multiple wicket types (LBW, caught)
- Custom graphics support via file path configuration

## Input Schema

Receives trajectory analysis data:

```json
{
  "label": "OUT",
  "confidence": 0.97,
  "decision_elements": {
    "wickets": "HITTING",
    "impact": "IN-LINE",
    "pitching": "OUTSIDE OFF"

  },
  "impact_point": {
    "x": 7.77,
    "y": 2.16,
    "z": 0.38,
    "speed": 125.6
  },
   "predicted_trajectory": [
    {
      "x": 5.44,
      "y": 1.63,
      "z": 0.5,
      "t": 0.68
    }, ...
  ],
  "bat_coordinates": [
    {
      "x": 1.75,
      "y": 0.65,
      "z": 0.5
    }, ...
  ],
  "stump_coordinates": [
    {
      "x": 2.3,
      "y": 0.1,
      "z": 0.1
    }, ...
  ]
}

```

## Output

Produces video with overlaid graphics showing:
- Color-coded trajectory segments (pre/post-bounce)
- Semi-transparent predicted path
- Impact point markers
- Decision indicators with confidence percentages

## Core Components

- **Interface Layer** - Standardized APIs for module integration
- **Decision Modules** - Separate logic for each wicket type
- **Animation Components** - Modular rendering for different ball phases
- **Coordinate Mapper** - 3D world to 2D video frame conversion
- **Graphics Engine** - Customizable overlay rendering system

Cricket DRS Overlay API

This Flask-based API provides two main endpoints for processing cricket videos and JSON data through a multi-module pipeline, returning the final overlaid video.

Features

Process cricket match videos and overlay decision review system (DRS) elements.

Accept raw JSON data representing frames and their metadata.

Handle video conversion to JSON frame data and reprocess it with overlays.

Endpoints

1. POST /api/process

Description: Accepts raw JSON data, runs it through enabled tracking and analysis modules, merges results, applies overlays, and returns the final video file.

Request Body: JSON payload representing precomputed frames or analysis data (see Accepted JSON Format below).

Response: video/mp4 file attachment of the processed video.

Example Request:

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

2. POST /api/convert-video

Description: Accepts a local video file path, converts frames to JSON, processes them through the same pipeline as /api/process, and returns the overlaid video.

Request Body: JSON object with a single field:

{
  "video_path": "path/to/input_cricket_video.mp4"
}

Response: video/mp4 file attachment of the processed video.

Accepted JSON Format

When sending JSON directly to /api/process, the API expects an array of frame objects, each containing:

frame_id (integer): Sequential identifier for the frame.

timestamp (string): Timecode in HH:MM:SS.mmm format.

image_data (string): Base64‑encoded JPEG image data of the frame.

metadata (object): Additional info, e.g., camera ID, player positions, etc.

Example JSON Payload:

[
  {
    "frame_id": 1,
    "timestamp": "00:00:00.000",
    "image_data": "/9j/4AAQSkZJRgABA...",
    "metadata": { "camera_id": "cam_1" }
  }
]

Error Handling

Standard HTTP status codes are returned.

JSON error details are provided when failures occur.

Installation

# Clone the repository
git clone https://github.com/your-username/cricket-drs-overlay-api.git

# Navigate to the project directory
cd cricket-drs-overlay-api

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate    # On Linux/Mac
venv\Scripts\activate       # On Windows

# Install dependencies
pip install -r requirements.txt

Running the Application

# Run the Flask application
python app.py

# The API will be available at:
http://127.0.0.1:5000

Future Improvements

Integration with live match feeds for real-time overlays.

Support for additional camera angles and ball-tracking analytics.

Enhanced error handling and logging mechanisms.

License

This project is licensed under the MIT License - see the LICENSE file for details.





