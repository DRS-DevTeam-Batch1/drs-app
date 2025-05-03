import sys
from typing import List, Tuple

import requests
import numpy as np

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


# ──────────────────────────────
#  3 × OUT  (≤0.15 m from stump centre @ 0,0,0.71)
# ──────────────────────────────
out_cases: List[Tuple[str, dict]] = [
    make_case("OUT-1 (inswing)",  (0.02,  0.02, 0.71), "inswing"),
    make_case("OUT-2 (outswing)", (-0.04, 0.04, 0.71), "outswing"),
    make_case("OUT-3 (straight)", (0.08,  0.00, 0.71), "none"),
]

# ──────────────────────────────
#  3 × NOT OUT  (>0.15 m away)
# ──────────────────────────────
not_out_cases: List[Tuple[str, dict]] = [
    make_case("N/O-1", (0.30,  0.31, 0.71), "inswing"),
    make_case("N/O-2", (-0.25, 0.25, 0.71), "outswing"),
    make_case("N/O-3", (0.18,  0.25, 0.71), "none"),
]

test_cases = out_cases + not_out_cases


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
            print(r.text)
            continue

        data = r.json()
        verdict = data.get("final_decision", "UNKNOWN")
        reason  = data.get("decision_reason", "")
        print(f"✅  {label:14s} → {verdict:7s} | {reason}")

    print("\nDone.")


if __name__ == "__main__":
    run_tests()
