# 🧠 Decision Making Module – DRS System

📌 Overview
The Decision Making Module is the brain of the ThirdEye DRS pipeline. It consolidates data from multiple sources—Trajectory Analysis, Bat's Edge Detection, and Ball & Object Tracking—to logically determine match outcomes like:

Out

Not Out

Edge Detected

It maps raw inputs into cricket rules, generates consistent outcomes, and prepares decision metadata for downstream visual rendering.

🔄 Position in Pipeline
    
    A[Trajectory Analysis Module] --> E[Decision Making Module]
    
    B[Bat's Edge Detection Module] --> E
    
    C[Ball and Object Tracking Module] --> E
    
    E --> F[Stream Analysis & Overlay Module]

📥 Input Data
This module consumes structured inputs in JSON from upstream modules:

🏏 From Trajectory Analysis Module:
trajectory: Ball path as a list of (x, y, z) coordinates

bouncePoint: Location where ball bounces

impactPoint: Where ball hits the pad

isHittingStumps: Boolean flag

pitchZone: Zone where the ball pitched (e.g., outside off)

🏏 From Bat's Edge Detection Module:
batEdgeDetected: true or false

contactFrame: Frame number where edge was detected

contactZone: Region of bat where contact happened

🏏 From Object Tracking Module:
bat_position: (x, y, z) of bat during swing

batsman_leg_position: (x, y, z) of pad

stump_coordinates: Real-world (x, y, z) coordinates of stumps

⚙️ Processing Flow
1. 🧠 Input Sync & Validation
Frame-wise synchronization of trajectory and edge detection

Data integrity checks for incomplete frames or missing metadata

2. ✨ Edge Detection First
If batEdgeDetected == true:

Final decision: "Edge Detected"

Skips LBW checks

Highlights contact point on bat

3. 👣 LBW Rule Evaluation
If no edge, apply LBW conditions:

Did the ball pitch in line or outside off?

Was the impact in line with stumps?

Would the ball hit the stumps?

Evaluates physics-based prediction from trajectory path

4. ✅ Decision Logic Tree
IF Edge Detected → "Edge Detected"
ELSE IF LBW Valid → "Out"
ELSE → "Not Out"
5. 🧩 Output Packaging
Final result: "Out" / "Not Out" / "Edge Detected"

Metadata:

Impact and bounce points

Decision label

Highlight toggles for UI

📤 Output Format
```
{
  "decision": "Out",
  "dismissalType": "LBW",
  "trajectory": [[x1, y1, z1], [x2, y2, z2], ...],
  "impactPoint": [x, y, z],
  "bouncePoint": [x, y, z],
  "batEdgeDetected": false,
  "frameTimestamp": 1302,
  "visualMarkers": {
    "highlightImpact": true,
    "stumpProjection": true,
    "decisionLabel": "Out"
  }
```

🧪 Testing and Validation
✅ Edge Scenarios: Tested against various swing/spin angles

✅ LBW Edge Cases: Pitched outside leg, missing stumps, low bounce

✅ Overlay Visuals: Manual review for alignment with ball path

✅ Debug Logs: Supports per-frame logging of decisions for replays
