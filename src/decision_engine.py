import math
from datetime import datetime
from typing import List

from src.models import (
    LBWInput,
    LBWOutput,
    Point3D,
    TrajectorySummary,
    VisualDecision,
    SwingAnalysisOutput,
    TrajectoryPoint,
)

# ──────────────────────────────
# Fixed ground-truth for a middle stump
# ──────────────────────────────
STUMP_CENTER = Point3D(x=0.0, y=0.0, z=0.71)   # 71 cm = top of stump
STUMP_RADIUS = 0.05                            # 5 cm radius for a “clean” hit


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


def _will_hit_stumps(path: List[TrajectoryPoint]) -> tuple[bool, float]:
    """
    Returns (is_hit, hit_percentage).

    A clean hit = 100%. Between stump edge (0.05m) and 0.15m we give a linear %
    to mimic Hawk-Eye confidence.
    """
    if not path:
        return False, 0.0

    end_point = path[-1]
    dist = _distance(end_point, STUMP_CENTER)

    if dist <= STUMP_RADIUS:
        return True, 100.0
    if dist <= 0.15:
        pct = max(
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


def process_decision(inp: LBWInput) -> LBWOutput:
    swing_type, swing_deg = _analyse_swing(inp.predicted_path)
    stump_hit, hit_pct = _will_hit_stumps(inp.predicted_path)

    swing_label = (
        f"{swing_type} swing ({swing_deg:.1f}°)" if swing_type != "none" else "no significant swing"
    )

    if stump_hit:
        final = "Out"
        reason = f"Ball projected to hit the stumps ({hit_pct:.1f}% overlap) {swing_label}"
    else:
        final = "Not Out"
        reason = f"Ball projected to miss the stumps {swing_label}"


    traj_sum = TrajectorySummary(
        initial_point=inp.predicted_path[0].model_dump(),
        final_point=inp.predicted_path[-1].model_dump(),
        closest_to_stumps=STUMP_CENTER.model_dump(),
        stump_hit_prediction=stump_hit,
    )


    visual = VisualDecision(
        highlight_path=True,
        highlight_miss_zone=not stump_hit,
        decision_overlay_color="red" if final == "Out" else "green",
    )

    return LBWOutput(
        timestamp=datetime.utcnow().isoformat(),
        final_decision=final,
        decision_reason=reason,
        trajectory_summary=traj_sum,
        visual_decision=visual,
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

