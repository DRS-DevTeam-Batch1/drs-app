
# Trajectory Analysis Module – Input & Output Schema

##  Module Overview

The **Trajectory Analysis Module** is the fourth module in the DRS (Decision Review System) pipeline. It is responsible for predicting the future path of the ball based on its current path. Once a significant portion of the ball's current path is tracked, the module predicts the future trajectory.

- Both **input** and **output** are lists of coordinates `(x, y, z, t)`
- `"t"` is an optional timestamp.
- This module **receives input from the Ball Tracking Module**
- The **predicted trajectory** is forwarded to the Decision Module.

---

##  Source of Input

- **Input Source**: Ball Tracking Module  
- The Ball’s trajectory and spin are tracked up to the current moment and passed here for prediction.

---

## Input Schema

Each input data point is a dictionary with:

| Field | Type  | Description                            |
|-------|-------|----------------------------------------|
| x     | float | Horizontal position of the ball        |
| y     | float | Vertical position (height) of the ball |
| z     | float | Lengthwise position (toward batsman)   |
| t     | time  | Timestamp (optional)                   |

## Example Input:
```json
[
  {"x": 2.4, "y": 1.2, "z": 0.6, "t": 0.1},
  {"x": 2.2, "y": 1.0, "z": 0.4, "t": 0.1}
]
```

---

## Output Schema

The module outputs a dictionary containing key physics-based predictions:

| Field           | Type           | Description                                           |
|-----------------|----------------|-------------------------------------------------------|
| predicted_path  | list of dicts  | Future ball path using the same format as input       |
| bounce_point    | dict           | The point where the ball bounces on the pitch         |
| swing_type      | string         | Type of swing: "inswing", "outswing", or "none"       |
| impact_location | dict           | Predicted point of impact on batsman (if any)         |

---

### Output Examples

#### Example 1:
```json
{
  "predicted_path": [
    {"x": 2.0, "y": 0.8, "z": 0.3, "t": 0.1},
    {"x": 1.8, "y": 0.6, "z": 0.2, "t": 0.1}
  ],
  "impact_location": {"x": 1.6, "y": 0.4, "z": 0.1},
  "bounce_point": {"x": 2.2, "y": 1.0, "z": 0.0},
  "swing_type": "inswing"
}
```

#### Example 2:
```json
{
  "predicted_path": [
    {"x": 2.1, "y": 0.7, "z": 0.3, "t": 0.05},
    {"x": 2.0, "y": 0.5, "z": 0.2, "t": 0.05}
  ],
  "impact_location": {"x": 1.9, "y": 0.3, "z": 0.1},
  "bounce_point": {"x": 2.3, "y": 1.1, "z": 0.0},
  "swing_type": "outswing"
}
```

#### Example 3:
```json
{
  "predicted_path": [
    {"x": 1.8, "y": 0.9, "z": 0.4, "t": 0.0},
    {"x": 1.7, "y": 0.6, "z": 0.3, "t": 0.0}
  ],
  "impact_location": {"x": 1.5, "y": 0.2, "z": 0.1},
  "bounce_point": {"x": 1.9, "y": 1.2, "z": 0.0},
  "swing_type": "none"
}
```

---

