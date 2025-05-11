markdown
# Trajectory Analysis API Documentation

## API Endpoint
POST /analyze_trajectory

## Request Schema
```json
{
  "bat_edge_detected": "boolean | Required",
  "ball_trajectory": [
    {
      "x": "float | Required (meters)",
      "y": "float | Required (meters)",
      "z": "float | Required (meters)",
      "t": "float | Required (seconds)"
    }
  ],
  "bat_position": {
    "x": "float | Required",
    "y": "float | Required",
    "z": "float | Required"
  },
  "batsman_leg_position": {
    "x": "float | Required",
    "y": "float | Required",
    "z": "float | Required"
  },
  "stump_coordinates": {
    "x": "float | Required",
    "y": "float | Required",
    "z": "float | Required"
  },
  // Optional fields (ignored in analysis)
  "contact_time": "float | Optional",
  "contact_distance": "float | Optional"
}
Response Schemas
Case 1: Bat Edge Detected
When: bat_edge_detected = true
Response:

json
{
  "decision": "NOT OUT",
  "reason": "Bat edge detected",
  // Optional fields echoed back
  "contact_time": "float | Optional",
  "contact_distance": "float | Optional"
}
Case 2: Trajectory Analysis Results
When: bat_edge_detected = false
Response:

json
{
  "decision": "OUT | NOT OUT",
  "confidence": "float (0.0-1.0)",
  "predicted_trajectory": [
    {
      "x": "float",
      "y": "float",
      "z": "float",
      "t": "float"
    }
  ],
  "impact_location": {
    "x": "float",
    "y": "float",
    "z": "float"
  },
  "bounce_point": {
    "x": "float",
    "y": "float",
    "z": "float",
    "t": "float"
  } | null,
  "swing_characteristics": {
    "lateral_movement": "float (meters)",
    "direction": "left-to-right | right-to-left | straight",
    "rate": "float (m/s)",
    "type": "conventional | reverse | none"
  }
}
Case 3: Error Responses
Status Code: 4xx or 5xx
Response:

json
{
  "error": "string",
  "missing_fields": ["string"] | Optional
}
Example Requests
Sample Input
json
{
  "bat_edge_detected": false,
  "ball_trajectory": [
    {"x": 0.45, "y": 0.9, "z": 0.3, "t": 0.01},
    {"x": 0.48, "y": 0.89, "z": 0.32, "t": 0.02}
  ],
  "bat_position": {"x": 0.49, "y": 0.885, "z": 0.325},
  "batsman_leg_position": {"x": 0.6, "y": 0.9, "z": 0.3},
  "stump_coordinates": {"x": 0.7, "y": 0.85, "z": 0.2},
  "contact_time": 0.01,
  "contact_distance": 0.049
}
Sample Success Response
json
{
  "decision": "OUT",
  "confidence": 0.82,
  "predicted_trajectory": [
    {"x": 0.45, "y": 0.9, "z": 0.3, "t": 0.01},
    {"x": 0.46, "y": 0.85, "z": 0.4, "t": 0.02}
  ],
  "impact_location": {"x": 0.6, "y": 0.9, "z": 0.3},
  "bounce_point": {"x": 0.3, "y": 0.5, "z": 0.0, "t": 0.005},
  "swing_characteristics": {
    "lateral_movement": 0.1,
    "direction": "right-to-left",
    "rate": 0.15,
    "type": "conventional"
  }
}
Sample Error Response
json
{
  "error": "Missing required fields",
  "missing_fields": ["stump_coordinates"]
}

import requests

payload = {
    "bat_edge_detected": False,
    "ball_trajectory": [{"x": 0.45, "y": 0.9, "z": 0.3, "t": 0.01}],
    "bat_position": {"x": 0.49, "y": 0.885, "z": 0.325},
    "batsman_leg_position": {"x": 0.6, "y": 0.9, "z": 0.3},
    "stump_coordinates": {"x": 0.7, "y": 0.85, "z": 0.2}
}

response = requests.post(
    "http://localhost:6051/analyze_trajectory",
    json=payload,
    headers={"Content-Type": "application/json"}
)

print(response.json())
