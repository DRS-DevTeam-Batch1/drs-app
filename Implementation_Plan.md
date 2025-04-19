# 🧠 Decision Making Module – DRS System

## Overview
The **Decision Making Module** is the core decision engine in the DRS (Decision Review System) pipeline. It gathers data from the **Trajectory Analysis**, **Bat's Edge Detection**, and **Object Tracking** modules to deliver a final verdict such as **"Out"**, **"Not Out"**, or **"Edge Detected"**. It applies cricket rules logically and precisely to ensure fair decisions and prepares the data for visual presentation.

---

## 🔄 Position in Pipeline

```mermaid
graph TD
    A[Trajectory Analysis Module] --> E[Decision Making Module]
    B[Bat's Edge Detection Module] --> E
    C[Ball and Object Tracking Module] --> E
    E --> F[Stream Analysis & Overlay Module]

📥 Input Data
This module consumes structured data from multiple previous modules:

From Trajectory Analysis Module:
Predicted ball path ((x, y, z) over time)

Bounce point and swing/spin metrics

Impact location (e.g., batsman’s pad)

From Bat's Edge Detection Module:
Boolean: batEdgeDetected (true or false)

Frame number of edge contact (if detected)

Location of edge on bat

Adjusted trajectory (if deflected)

From Ball & Object Tracking Module:
Batsman’s leg position and stance

Stump coordinates and height

⚙️ Processing Flow
The module performs the following steps:

Edge Detection Check

If batEdgeDetected == true, the final decision is "Edge Detected"

Trajectory analysis is skipped for LBW

Passes along visual marker for edge highlight

LBW Decision Making (If No Edge)

Checks if the ball hit the batsman's pad

Validates conditions for LBW:

Ball pitched in line or outside off

Impact in line with stumps

Ball would have hit the stumps

Predicts result using trajectory and physics data

Final Rule Application

Prioritizes Edge > LBW

Decision outcomes:

"Out"

"Not Out"

"Edge Detected"

Metadata Packaging

Assembles trajectory points, impact coordinates, and decision labels

Builds a data object for overlay visualization

📤 Output
The module sends the following to Module 6: Stream Analysis & Overlay:

json
Copy
Edit
{
  "decision": "Out",
  "dismissalType": "LBW",
  "trajectory": [[x1,y1,z1], [x2,y2,z2], ...],
  "impactPoint": [x, y, z],
  "bouncePoint": [x, y, z],
  "batEdgeDetected": false,
  "frameTimestamp": 1302,
  "visualMarkers": {
    "highlightImpact": true,
    "stumpProjection": true,
    "decisionLabel": "Out"
  }
}
🧪 Testing and Validation
Rule engine tested on known cricket scenarios

LBW edge cases tested against multiple ball paths

Manual verification of overlay alignment for visual accuracy

Debug mode supports JSON log outputs per frame

🚀 Future Extensions
Integrate confidence scoring via ML for uncertain decisions

Expand support for more dismissal types (e.g., Caught, Bowled)

Use real player calibration data for accuracy

