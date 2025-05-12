### Base Configuration  
**Default Port**: `6051` (customize via `PORT` environment variable)  
**Base URL**: `http://your-server:6051`

---

## Core Features  

### 1. Service Health Check  
**Endpoint**: `GET /health`  

```json  
// Sample Response  
{
  "status": "healthy",
  "module": "trajectory-analysis"
}
```
**When to Use**:  
- Quick verification that the service is operational  
- Returns `healthy` if ready to process requests  

---

### 2. LBW Decision Predictor  
**Endpoint**: `POST /analyze_trajectory`  

####  Required Input  
```json  
{
  "bat_edge_detected": false,
  "ball_trajectory": [ /* 3D positions over time */ ],
  "bat_position": { "x": 0.6, "y": 0.8, "z": 16.0 },
  "batsman_leg_position": { "x": 0.5, "y": 0.9, "z": 15.0 },
  "stump_coordinates": { "x": 0.7, "y": 0.0, "z": 20.0 }
}
```

#### Key Parameters Explained  
| Field                  | Purpose                                  |  
|------------------------|------------------------------------------|  
| `bat_edge_detected`    | Must be `false` to activate LBW analysis |  
| `ball_trajectory`      | Sequential 3D positions (x,y,z) + timestamp |  
| `stump_coordinates`    | Target wicket's 3D location              |  

#### Sample Output  
```json  
{
  "decision": "OUT",
  "confidence": 0.82,
  "predicted_trajectory": [ /* Projected path */ ],
  "impact_location": { "x": 0.5, "y": 0.9, "z": 15.0 },
  "bounce_point": { "x": 0.3, "y": 0.5, "z": 10.0, "t": 0.5 },
  "swing_characteristics": {
    "lateral_movement": 0.1,
    "direction": "right-to-left",
    "type": "conventional swing"
  }
}
```

#### Understanding Results  
- **Confidence Score**: 0-1 likelihood of accurate prediction  
- **Swing Analysis**: Identifies ball movement type/direction  
- **Impact Location**: Where ball would hit batsman/bat  

---

### 3. Trajectory Visualizer (Optional)  
**Endpoint**: `POST /visualize_trajectory`  

```json  
// Sample Response  
{
  "status": "success",
  "visualization_path": "trajectory_visualization.png"
}
```
**Use Case**:  
- Generate 3D graphs for coaching/review sessions  
- Debug unusual trajectory patterns  

---

## Error Handling  
| Code | Scenario                     | Solution                          |  
|------|------------------------------|-----------------------------------|  
| 400  | Missing required fields      | Verify all input parameters       |  
| 500  | Internal server error        | Check service logs/restart        |  

---

##  Implementation Tips  
1. **Coordinate System**: All positions in meters from pitch origin  
2. **Time Increments**: `t` values in seconds with 0.1s resolution  
3. **Edge Detection**: Use separate ball-tracking systems before invoking this API  

This API empowers umpires and coaches with real-time lbw predictions using advanced physics modeling. Let’s revolutionize cricket decisions together!

---
