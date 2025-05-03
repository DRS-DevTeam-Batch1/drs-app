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



