# Decision Making Module – DRS System

The Decision Making Module serves as the core logic engine of the ThirdEye DRS pipeline. It integrates data from multiple upstream modules—Trajectory Analysis, Bat Edge Detection, and Ball & Object Tracking—to logically determine match outcomes such as:

Out
Not Out
Edge Detected

This module maps structured inputs to cricket rules, applies decision logic, and prepares output metadata for downstream rendering during live or replay broadcasts.

🔄 Position in the Pipeline
graph TD
A[Trajectory Analysis Module] --> E[Decision Making Module]
B[Bat's Edge Detection Module] --> E
C[Ball & Object Tracking Module] --> E
E --> F[Stream Analysis & Overlay Module]
📥 Input Data
The module consumes structured JSON inputs from upstream modules:

🏏 From Trajectory Analysis Module
trajectory: Ball path as a list of (x, y, z) coordinates

bouncePoint: Location where the ball bounces

impactPoint: Location where the ball hits the pad

isHittingStumps: Boolean flag indicating whether the ball will hit the stumps

pitchZone: Area where the ball pitched (e.g., outside off, in-line)

🏏 From Bat Edge Detection Module
batEdgeDetected: true or false

contactFrame: Frame number where the bat edge was detected

contactZone: Region on the bat where contact was detected

🏏 From Object Tracking Module
bat_position: (x, y, z) of the bat during the swing

batsman_leg_position: (x, y, z) position of the batsman's leg/pad

stump_coordinates: Real-world (x, y, z) coordinates of the stumps

⚙️ Processing Flow
🧠 1. Input Sync & Validation
Synchronizes data across modules on a per-frame basis

Validates input integrity and checks for any missing or malformed metadata

✨ 2. Edge Detection First
If batEdgeDetected == true:

The decision is immediately set to "Edge Detected"

LBW evaluation is skipped

Contact point on the bat is highlighted in the output

3. LBW Rule Evaluation (If No Edge)
   If no edge is detected, LBW conditions are evaluated:

Did the ball pitch in line or outside off?

Was the impact in line with the stumps?

Is the ball predicted to hit the stumps?

This uses physics-based modeling from the trajectory data to evaluate the dismissal validity.

Decision Logic Tree

IF batEdgeDetected → "Edge Detected"
ELSE IF LBW Valid → "Out"
ELSE → "Not Out"
🧩 Output Packaging
The final result is structured and returned as JSON with both the decision and supporting metadata.

📤 Output Format
json
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
}
🧪 Testing and Validation
✅ Edge Scenarios: Validated with various spin and swing angles

✅ LBW Edge Cases: Includes testing for edge situations like pitching outside leg, missing stumps, and low bounce

✅ Overlay Visuals: Manually reviewed to confirm alignment with ball trajectory

✅ Debug Logs: Frame-level logs maintained to support replay validation and debugging
