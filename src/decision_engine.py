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

from math import isclose

def check_edge_cases(bounce_point: Point3D, impact_point: Point3D, leg_position: Point3D, stump_coords: List[Point3D]) -> dict:
    result = {
        "auto_not_out": False,
        "no_bounce_detected": False,
        "umpires_call_flag": False,
        "decision_confidence": 1.0
    }

    # pitched outside leg stump
    stump_x_values = [stump.x for stump in stump_coords]
    middle_stump_x = sum(stump_x_values) / len(stump_x_values)
    leg_side = middle_stump_x - 0.2  # 0.2 margin for left leg zone
    
    if bounce_point.x < leg_side:
        result["auto_not_out"] = True
        result["decision_confidence"] = 1.0
        return result

    #  no bounce detected, it's a full toss
    if isclose(bounce_point.z, impact_point.z, abs_tol=0.01): 
        result["no_bounce_detected"] = True
        result["decision_confidence"] = 0.85


    return result


from datetime import datetime

def process_decision(inp: LBWInput, leg_position: Point3D, stump_coordinates: List[Point3D]) -> LBWOutput:
    swing_type, swing_deg = _analyse_swing(inp.predicted_path)
    stump_hit, hit_pct = _will_hit_stumps(inp.predicted_path)

    swing_label = (
        f"{swing_type} swing ({swing_deg:.1f}°)" if swing_type != "none" else "no significant swing"
    )

    edge = check_edge_cases(
        bounce_point=inp.bounce_point,
        impact_point=inp.impact_location,
        leg_position=leg_position,
        stump_coords=stump_coordinates
    )

    if edge["auto_not_out"]:
        final = "Not Out"
        reason = "Ball pitched outside leg stump"
    elif edge["no_bounce_detected"]:
        final = "Review Suggested"
        reason = "Full toss or bounce undetected"
    elif edge["umpires_call_flag"]:
        final = "Umpire's Call"
        reason = "Bat and pad overlap"
    elif stump_hit:
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
        decision_confidence=edge["decision_confidence"],
        umpires_call_flag=edge["umpires_call_flag"],
        trajectory_summary=traj_sum,
        visual_decision=visual,
    )


def analyse_swing_detailed(inp: LBWInput) -> SwingAnalysisOutput:
    swing_type = inp.swing_type
    _, swing_degree = _analyse_swing(inp.predicted_path)

    first, last = inp.predicted_path[0], inp.predicted_path[-1]
    deviation = _distance(first, last)
    dangerous = deviation > 0.5 and swing_degree > 3.0

    recommended = {
        "inswing": "straight drive",
        "outswing": "cover drive",
    }.get(swing_type, "straight bat")

    impact_info = {
        "position": inp.impact_location.model_dump(),
        "velocity": _velocity(inp.predicted_path),
        "angle": _angle(inp.predicted_path),
    }

    return SwingAnalysisOutput(
        swing_type=swing_type,
        swing_degree=swing_degree,
        predicted_deviation=deviation,
        impact_analysis=impact_info,
        is_dangerous_delivery=dangerous,
        recommended_shot=recommended,
    )
