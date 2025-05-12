1. Health Check
Endpoint:
GET /health

Request:
No body required

Response:

json
{
  "status": "healthy",
  "module": "trajectory-analysis"
}
Purpose:
Verify if the service is running.

2. LBW Decision Analysis
Endpoint:
POST /analyze_trajectory

Request Body:

json
{
  "bat_edge_detected": false,
  "ball_trajectory": [
    {"x": 0.1, "y": 1.8, "z": 0.0, "t": 0.0},
    {"x": 0.15, "y": 1.7, "z": 2.0, "t": 0.1},
    ...
  ],
  "bat_position": {"x": 0.6, "y": 0.8, "z": 16.0},
  "batsman_leg_position": {"x": 0.5, "y": 0.9, "z": 15.0},
  "stump_coordinates": {"x": 0.7, "y": 0.0, "z": 20.0}
}
Response:

json
{
  "decision": "OUT",
  "confidence": 0.82,
  "predicted_trajectory": [
    {"x": 0.45, "y": 0.9, "z": 15.0, "t": 0.7},
    {"x": 0.46, "y": 0.85, "z": 16.2, "t": 0.8},
    ...
  ],
  "impact_location": {"x": 0.5, "y": 0.9, "z": 15.0},
  "bounce_point": {"x": 0.3, "y": 0.5, "z": 10.0, "t": 0.5},
  "swing_characteristics": {
    "lateral_movement": 0.1,
    "direction": "right-to-left",
    "rate": 0.15,
    "type": "conventional swing"
  }
}
Purpose:
Predict whether the ball would hit the stumps (LBW decision) after analyzing trajectory, bounce, and swing.

3. Trajectory Visualization (Optional)
Endpoint:
POST /visualize_trajectory

Request Body:

json
{
  "ball_trajectory": [
    {"x": 0.1, "y": 1.8, "z": 0.0, "t": 0.0},
    {"x": 0.15, "y": 1.7, "z": 2.0, "t": 0.1},
    ...
  ]
}
Response:

json
{
  "status": "success",
  "visualization_path": "trajectory_visualization.png"
}
Purpose:
Generate a 3D plot of the ball’s trajectory (for debugging/analysis).



Required Fields:

bat_edge_detected must be false to trigger trajectory analysis.

ball_trajectory, bat_position, batsman_leg_position, and stump_coordinates are mandatory.

Error Handling:

Returns 400 if fields are missing.

Returns 500 for internal errors (e.g., model loading failures).

Default Port:
The service runs on 6051 unless overridden via the PORT environment variable.
