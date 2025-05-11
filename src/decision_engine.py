"""Decision Engine for LBW (Leg Before Wicket) analysis in cricket.

This module contains the core logic for analyzing ball trajectories and making
LBW decisions based on projected paths and swing characteristics.
"""
import math
from datetime import datetime
from typing import List, Tuple

from src.models import (
    LBWInput,
    LBWOutput,
    Point3D,
    TrajectorySummary,
    SwingAnalysisOutput,
    VisualDecision,
    TrajectoryPoint,
)

# ──────────────────────────────────────────────────────
# Fixed ground-truth constants for a middle stump
# ──────────────────────────────────────────────────────
STUMP_CENTER: Point3D = Point3D(x=0.0, y=0.0, z=0.71)  # 71 cm = top of stump
STUMP_RADIUS: float = 0.05  # 5 cm radius for a "clean" hit


# ──────────────────────────────
# Small maths helpers
# ──────────────────────────────
def _distance(p1: Point3D, p2: Point3D) -> float:
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2 + (p1.z - p2.z) ** 2) ** 0.5


def _velocity(path: List[TrajectoryPoint]) -> float:
    """Straight-line average velocity between first and last sample (m · s-1)."""
    if len(path) < 2:
        return 0.0
    first, last = path[0], path[-1]
    dt = last.t - first.t
    return _distance(first, last) / dt if dt > 0 else 0.0


def _angle(path: List[TrajectoryPoint]) -> float:
    """Heading in the horizontal (XY) plane at impact (degrees)."""
    if len(path) < 2:
        return 0.0
    first, last = path[0], path[-1]
    dx, dy = last.x - first.x, last.y - first.y
    return math.degrees(math.atan2(dy, dx))


def _will_hit_stumps(path: List[TrajectoryPoint]) -> Tuple[bool, float]:
    """
    Returns (is_hit, hit_percentage).

    A clean hit = 100%. Between stump edge (0.05m) and 0.15m we give a linear %
    to mimic Hawk-Eye confidence.
    """
    if not path:
        return False, 0.0

    end_point: TrajectoryPoint = path[-1]
    dist: float = _distance(end_point, STUMP_CENTER)

    if dist <= STUMP_RADIUS:
        return True, 100.0
    if dist <= 0.15:
        pct: float = max(
            0.0,
            100.0 * (1.0 - (dist - STUMP_RADIUS) / (0.15 - STUMP_RADIUS)),
        )
        return pct > 0.0, pct
    return False, 0.0

def _analyse_swing(path: List[TrajectoryPoint]) -> tuple[str, float]:
    """
    (swing_type, swing_degree)

    Uses the mid-point deviation from the straight line joining the first and
    last samples.  Guards against zero X-displacement to avoid div-by-zero.
    """
    if len(path) < 3:
        return "none", 0.0

    first, mid, last = path[0], path[len(path) // 2], path[-1]
    dx_total = last.x - first.x
    dy_total = last.y - first.y

    if abs(dx_total) < 1e-6:
        deviation = 0.0
    else:
        expected_y = first.y + dy_total * (mid.x - first.x) / dx_total
        deviation = mid.y - expected_y

    if deviation > 0.05:
        return "outswing", abs(deviation) * 10.0
    if deviation < -0.05:
        return "inswing", abs(deviation) * 10.0
    return "none", abs(deviation) * 10.0

def process_decision(input_data: LBWInput) -> LBWOutput:
    swing_type, swing_angle = _analyse_swing(input_data.predicted_path)
    will_hit_stumps, overlap_percentage = _will_hit_stumps(input_data.predicted_path)

    if swing_type != "none":
        swing_description = f"{swing_type} swing ({swing_angle:.1f}°)"
    else:
        swing_description = "no significant swing"

    if will_hit_stumps:
        decision = "Out"
        explanation = f"Ball projected to hit the stumps ({overlap_percentage:.1f}% overlap) {swing_description}"
    else:
        decision = "Not Out"
        explanation = f"Ball projected to miss the stumps {swing_description}"

    trajectory = TrajectorySummary(
        initial_point=input_data.predicted_path[0].model_dump(),
        final_point=input_data.predicted_path[-1].model_dump(),
        closest_to_stumps=STUMP_CENTER.model_dump(),
        stump_hit_prediction=will_hit_stumps
    )

    visuals = VisualDecision(
        highlight_path=True,
        highlight_miss_zone=not will_hit_stumps,
        decision_overlay_color="red" if decision == "Out" else "green"
    )

    return LBWOutput(
        timestamp=datetime.utcnow().isoformat(),
        final_decision=decision,
        decision_reason=explanation,
        trajectory_summary=trajectory,
        visual_decision=visuals
    )


def analyze_swing_detailed(input_data: LBWInput) -> SwingAnalysisOutput:
    swing_type = input_data.swing_type
    _, degree_of_swing = _analyse_swing(input_data.predicted_path)

    start_point = input_data.predicted_path[0]
    end_point = input_data.predicted_path[-1]
    deviation = _distance(start_point, end_point)

    is_dangerous = deviation > 0.5 and degree_of_swing > 3.0

    shot_suggestion = {
        "inswing": "straight drive",
        "outswing": "cover drive"
    }.get(swing_type, "straight bat")

    impact_details = {
        "position": input_data.impact_location.model_dump(),
        "velocity": _velocity(input_data.predicted_path),
        "angle": _angle(input_data.predicted_path)
    }

    return SwingAnalysisOutput(
        swing_type=swing_type,
        swing_degree=degree_of_swing,
        predicted_deviation=deviation,
        impact_analysis=impact_details,
        is_dangerous_delivery=is_dangerous,
        recommended_shot=shot_suggestion
    )

