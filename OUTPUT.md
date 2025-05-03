# Cricket DRS API – Sample LBW Decision Output

Below is a real response returned from `POST /api/lbw‑decision` for a ball that was **given out**.  
The section afterward walks through every field and why it has its value.

## Example JSON response

```json
{
  "decision_reason": "Ball projected to hit the stumps (100.0% overlap) no significant swing",
  "final_decision": "Out",
  "timestamp": "2025-05-03T06:44:00.961750",
  "trajectory_summary": {
    "closest_to_stumps": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.71
    },
    "final_point": {
      "t": 0.8,
      "x": 0.02,
      "y": 0.02,
      "z": 0.71
    },
    "initial_point": {
      "t": 0.0,
      "x": 0.3,
      "y": 1.5,
      "z": 1.0
    },
    "stump_hit_prediction": true
  },
  "visual_decision": {
    "decision_overlay_color": "red",
    "highlight_miss_zone": false,
    "highlight_path": true
  }
}
```

---

## JSON field‑by‑field explanation

### Top‑level keys

| Key                      | Sample value                                                               | Meaning                                                                         |
| ------------------------ | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **`timestamp`**          | `2025‑05‑03T06:44:00.961750`                                               | UTC time when the engine produced the verdict.                                  |
| **`final_decision`**     | `"Out"`                                                                    | LBW decision. Either **`Out`** or **`Not Out`**.                                |
| **`decision_reason`**    | `"Ball projected to hit the stumps (100.0% overlap) no significant swing"` | Human‑readable justification. Combines stump‑hit percentage with swing summary. |
| **`ball_contact`**       | object                                                                     | Flags for bat/leg/edge contact (all `false` in this minimal build).             |
| **`trajectory_summary`** | object                                                                     | Compact description of the ball path and stump prediction.                      |
| **`visual_decision`**    | object                                                                     | UI hints for drawing overlays in a broadcast package.                           |

### `trajectory_summary`

| Key                    | Meaning                                                      |
| ---------------------- | ------------------------------------------------------------ |
| `initial_point`        | First sample in the predicted path (release).                |
| `final_point`          | Last sample, i.e. projected location at the stumps.          |
| `closest_to_stumps`    | Fixed centre of the middle stump `(0, 0, 0.71)`.             |
| `stump_hit_prediction` | `true` if the last point lies within 0.15 m of stump centre. |

### `visual_decision`

| Key                      | Meaning                                          |
| ------------------------ | ------------------------------------------------ |
| `decision_overlay_color` | `"red"` for **Out**, `"green"` for **Not Out**.  |
| `highlight_path`         | Draw the ball’s path polyline.                   |
| `highlight_miss_zone`    | Shade the “missing” area (only for **Not Out**). |

---

### How to read it quickly

> **Out** because the ball’s centre ends < 5 cm from stump centre  
> (100 % overlap), and there was _no detectable bat contact or swing_  
> that would change the verdict.
