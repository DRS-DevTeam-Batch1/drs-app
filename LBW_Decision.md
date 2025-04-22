# 🧠 Decision Making Module - DRS System

Welcome to the **Decision Making Module** of the Cricket DRS (Decision Review System) Project! This module analyzes bat contact, predicted trajectory, and player/stump positions to determine the final umpiring decision. 🏏

---

## 📌 Overview

The Decision Making Module consolidates inputs from multiple upstream modules to render a final decision (Out, Not Out, Edge Detected) based on cricket rules and trajectory analysis.

---

## 🛠 Inputs

This module receives structured data from previous stages:

- 🔄 **Bat Edge Detection Module**
  - `bat_contact: bool`
- 📍 **Trajectory Analysis Module**
  - `predicted_trajectory: List[(x, y, z)]`
  - `impact_location: (x, y)`
  - `bounce_point: (x, y)`
  - `swing_characteristics: {spin: float, swing_angle: float}`
- 🧍‍♂️ **Player and Stump Tracking**
  - `batsman_leg_position: (x, y)`
  - `stump_position: (x, y)`

---

## 📤 Outputs

The final result will be:

- ✅ `decision: str` — (Out / Not Out / Edge Detected)
- 🖼️ `decision_metadata: dict` — Data to be visualized on stream
  - Includes trajectory overlay, impact marker, bat edge indicator, etc.

---

## ⚙️ LBW Decision Logic

### 📥 Step 1: Parse Trajectory Output

````python
impact_x, impact_y = impact_location
ball_path = predicted_trajectory

# 🧩 Step 2: Extract Parameters

- **Bat Contact**:
  - Check if the ball has made contact with the bat.
  - `bat_contact: bool`

- **Ball's Impact Location**:
  - The location where the ball is predicted to hit.
  - `impact_location: (x, y)`

- **Ball Trajectory**:
  - The predicted 3D coordinates of the ball's path.
  - `predicted_trajectory: List[(x, y, z)]`

- **Bounce Point**:
  - The location where the ball bounces.
  - `bounce_point: (x, y)`

- **Player and Stump Positions**:
  - Batsman and stump positions.
  - `batsman_leg_position: (x, y)`
  - `stump_position: (x, y)`

---

### 📝 Sample Code to Extract Parameters:

```python
impact_x, impact_y = impact_location
ball_path = predicted_trajectory
bounce_x, bounce_y = bounce_point
batsman_position = batsman_leg_position
stump_position = stump_position

# Is the ball predicted to hit stumps?
will_hit_stumps = check_if_ball_hits_stumps(impact_x, impact_y, stump_position)
````
