import sys
from typing import List, Tuple, Dict, Any

import requests
import numpy as np

from src.decision_engine import STUMP_HALF_DEPTH

API_URL = "http://localhost:8000/api/lbw-decision"

def make_case(
    label: str,
    final_xyz: Tuple[float, float, float],
    swing_type: str = "none",
    n_points: int = 12,
    t_first: float = 0.0,
    t_last: float = 0.8,
) -> Tuple[str, dict]:
    """
    Create a payload whose predicted_path has `n_points` samples
    (linear interpolation between release → final).
    """

    start = np.array([0.30, 1.50, 1.00])
    end   = np.array(final_xyz)

    xs = np.linspace(start[0], end[0], n_points)
    ys = np.linspace(start[1], end[1], n_points)
    zs = np.linspace(start[2], end[2], n_points)
    ts = np.linspace(t_first, t_last, n_points)

    path = [
        {"x": float(x), "y": float(y), "z": float(z), "t": float(t)}
        for x, y, z, t in zip(xs, ys, zs, ts)
    ]

    impact_pt = path[-2]

    bounce_idx = int(0.4 * (n_points - 1))
    bounce_raw = path[bounce_idx]
    bounce_pt = {"x": bounce_raw["x"], "y": bounce_raw["y"], "z": 0.0}

    return (
        label,
        {
            "predicted_path": path,
            "impact_location": impact_pt,
            "bounce_point": bounce_pt,
            "swing_type": swing_type,
        },
    )

def make_bounce_outside_leg_case(label: str, bounce_y: float):
    return label, {
        # ... all other fields None or omitted per your model defaults ...
        "bounce_point": {"x": 0.4, "y": bounce_y, "z": 0.0}
    }



def make_type1_case(label: str) -> Tuple[str, dict]:
    """Create a Type 1 input case with trajectory and swing characteristics."""
    return (
        label,
        {
            "bounce_point": None,
            "confidence": 0.6,
            "decision": "NOT OUT",
            "impact_location": {"x": 0.6, "y": 0.9, "z": 0.3},
            "predicted_trajectory": [
                {"t": 0.04, "x": 0.6, "y": 0.9, "z": 0.3},
                {"t": 0.03999043062200957, "x": 0.5999808612440191, "y": 0.9000095689288249, "z": 0.29473684210526263},
                {"t": 0.03998086124401914, "x": 0.5999617224880383, "y": 0.9000191369593188, "z": 0.2894736842105253},
                {"t": 0.039971291866028706, "x": 0.5999425837320573, "y": 0.9000287040914814, "z": 0.2842105263157879},
                {"t": 0.03996172248803828, "x": 0.5999234449760765, "y": 0.9000382703253131, "z": 0.2789473684210544},
                {"t": 0.03995215311004785, "x": 0.5999043062200957, "y": 0.9000478356608137, "z": 0.27368421052631703},
                {"t": 0.03994258373205742, "x": 0.5998851674641148, "y": 0.9000574000979831, "z": 0.26842105263157967},
                {"t": 0.03993301435406699, "x": 0.599866028708134, "y": 0.9000669636368215, "z": 0.2631578947368423},
                {"t": 0.039923444976076555, "x": 0.5998468899521531, "y": 0.9000765262773288, "z": 0.25789473684210495},
                {"t": 0.039913875598086124, "x": 0.5998277511961723, "y": 0.9000860880195051, "z": 0.2526315789473676},
                {"t": 0.0399043062200957, "x": 0.5998086124401913, "y": 0.9000956488633501, "z": 0.24736842105263407},
                {"t": 0.03989473684210527, "x": 0.5997894736842105, "y": 0.9001052088088642, "z": 0.2421052631578967},
                {"t": 0.039885167464114836, "x": 0.5997703349282296, "y": 0.9001147678560473, "z": 0.23684210526315935},
                {"t": 0.039875598086124404, "x": 0.5997511961722488, "y": 0.9001243260048992, "z": 0.231578947368422},
                {"t": 0.03986602870813397, "x": 0.5997320574162679, "y": 0.90013388325542, "z": 0.22631578947368464},
                {"t": 0.03985645933014354, "x": 0.5997129186602871, "y": 0.9001434396076097, "z": 0.22105263157894728},
                {"t": 0.03984688995215312, "x": 0.5996937799043062, "y": 0.9001529950614684, "z": 0.21578947368421372},
                {"t": 0.039837320574162685, "x": 0.5996746411483254, "y": 0.900162549616996, "z": 0.21052631578947636},
                {"t": 0.039827751196172254, "x": 0.5996555023923444, "y": 0.9001721032741924, "z": 0.205263157894739},
                {"t": 0.03981818181818182, "x": 0.5996363636363636, "y": 0.9001816560330579, "z": 0.20000000000000165}
            ],
            "swing_characteristics": {
                "direction": "right-to-left",
                "lateral_movement": 0.07,
                "rate": 2.3333333333333335
            }
        }
    )

def make_type2_case(label: str) -> Tuple[str, dict]:
    """Create a Type 2 input case with just decision and reason."""
    return (
        label,
        {
            "decision": "NOT OUT",
            "reason": "Bat edge detected"
        }
    )

def make_type3_case(label: str) -> Tuple[str, dict]:
    """
    Generate a Type 3 case representing a bat edge detection scenario
    with associated ball trajectory and positional data.
    """
    return (
        label,
        {
            "bat_edge_detected": True,
            "contact_time": 0.01,
            "contact_distance": 0.049497474683058325,
            "ball_trajectory": [
                {"x": 0.45, "y": 0.9, "z": 0.3, "t": 0.01},
                {"x": 0.48, "y": 0.89, "z": 0.32, "t": 0.02},
                {"x": 0.5, "y": 0.88, "z": 0.33, "t": 0.03}
            ],
            "bat_position": {"x": 0.49, "y": 0.885, "z": 0.325},
            "batsman_leg_position": {"x": 0.6, "y": 0.9, "z": 0.3},
            "stump_coordinates": {"x": 0.7, "y": 0.85, "z": 0.2}
        }
    )
# ──────────────────────────────
#  Original test cases (legacy format)
# ──────────────────────────────
out_cases: List[Tuple[str, dict]] = [
    make_case("OUT-1 (inswing)",  (0.02,  0.02, 0.71), "inswing"),
    make_case("OUT-2 (outswing)", (-0.04, 0.04, 0.71), "outswing"),
    make_case("OUT-3 (straight)", (0.08,  0.00, 0.71), "none"),
]

not_out_cases: List[Tuple[str, dict]] = [
    make_case("N/O-1", (0.30,  0.31, 0.71), "inswing"),
    make_case("N/O-2", (-0.25, 0.25, 0.71), "outswing"),
    make_case("N/O-3", (0.18,  0.25, 0.71), "none"),
]

# ──────────────────────────────
#  New test cases (new formats)
# ──────────────────────────────
new_format_cases: List[Tuple[str, dict]] = [
    make_type1_case("Type1-Trajectory"),
    make_type2_case("Type2-Simple"),
    make_type3_case("Type3-BatEdge"),
]



# Combine all test cases
test_cases = out_cases + not_out_cases + new_format_cases

leg_line = 0.0 - STUMP_HALF_DEPTH  # e.g., -0.02
bounce_out_cases = [
    make_bounce_outside_leg_case("Pitch-O-1", leg_line - 0.01),
    make_bounce_outside_leg_case("Pitch-O-2", leg_line - 0.02),
    make_bounce_outside_leg_case("Pitch-O-3", leg_line - 0.05),
]
test_cases += bounce_out_cases

# ──────────────────────────────
# Execute
# ──────────────────────────────
def run_tests():
    print(f"Posting {len(test_cases)} trajectories to {API_URL}\n")

    for label, payload in test_cases:
        try:
            r = requests.post(API_URL, json=payload, timeout=5)
        except Exception as exc:
            sys.exit(f"❌  Request for {label} failed: {exc}")

        if r.status_code != 200:
            print(f"❌  {label:14s} → HTTP {r.status_code}")
            continue

        data = r.json()
        verdict = data.get("final_decision", "UNKNOWN")
        reason  = data.get("decision_reason", "")
        print(f"✅  {label:14s} → {verdict:7s} | {reason}")

    print("\nDone.")


if __name__ == "__main__":
    run_tests()
