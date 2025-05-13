"""Decision Engine for LBW (Leg Before Wicket) analysis in cricket.

This module contains the core logic for analyzing ball trajectories and making
LBW decisions based on projected paths and swing characteristics.
"""
import math
from datetime import datetime
from typing import List, Tuple, Optional

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
# Fixed ground-truth constants for a middle stump (box model)
# ──────────────────────────────────────────────────────
STUMP_CENTER: Point3D = Point3D(x=0.0, y=0.0, z=0.71)  # 71 cm = top of stump
# Box half dimensions (meters): width along X, depth along Y
STUMP_HALF_WIDTH: float = 0.05  # 5 cm half-width
STUMP_HALF_DEPTH: float = 0.02  # 2 cm half-depth (stump thickness)
# Margin for confidence calculation
STUMP_MARGIN: float = 0.10  # 10 cm beyond box for linear confidence

# ──────────────────────────────
# Small maths helpers
# ──────────────────────────────
def _distance(p1: Point3D, p2: Point3D) -> float:
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2 + (p1.z - p2.z) ** 2) ** 0.5

# (velocity and angle helpers unchanged...)

def _velocity(path: List[TrajectoryPoint]) -> float:
    if len(path) < 2:
        return 0.0
    first, last = path[0], path[-1]
    dt = last.t - first.t
    return _distance(first, last) / dt if dt > 0 else 0.0


def _angle(path: List[TrajectoryPoint]) -> float:
    if len(path) < 2:
        return 0.0
    first, last = path[0], path[-1]
    dx, dy = last.x - first.x, last.y - first.y
    return math.degrees(math.atan2(dy, dx))


def _will_hit_stumps(path: List[TrajectoryPoint]) -> Tuple[bool, float]:
    """
    Returns (is_hit, hit_percentage) using a box model around the stumps.
    A clean hit = 100%. Within STUMP_MARGIN beyond the box gives linear confidence.
    """
    if not path:
        return False, 0.0

    end_pt: TrajectoryPoint = path[-1]
    dx = abs(end_pt.x - STUMP_CENTER.x)
    dy = abs(end_pt.y - STUMP_CENTER.y)

    # Check within box for clean hit
    if dx <= STUMP_HALF_WIDTH and dy <= STUMP_HALF_DEPTH:
        return True, 100.0
    # Check within margin region for confidence
    if dx <= STUMP_HALF_WIDTH + STUMP_MARGIN and dy <= STUMP_HALF_DEPTH + STUMP_MARGIN:
        # Compute normalized margin distance beyond box
        mx = max(0.0, dx - STUMP_HALF_WIDTH)
        my = max(0.0, dy - STUMP_HALF_DEPTH)
        # use the larger of the two normalized distances
        norm = max(mx / STUMP_MARGIN, my / STUMP_MARGIN)
        confidence = max(0.0, 100.0 * (1.0 - norm))
        return confidence > 0.0, confidence
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
    """
    Process the input data and make a decision based on the input type.
    
    The function handles three types of inputs:
    1. Trajectory-based input with predicted path and swing characteristics
    2. Simple decision with just decision and reason
    3. Bat edge detection input with ball trajectory and bat position
    """

    if input_data.bounce_point is not None:
        bp_y = input_data.bounce_point.y
        # leg stump line (right-hander) at y = STUMP_CENTER.y - STUMP_HALF_DEPTH
        leg_line = STUMP_CENTER.y - STUMP_HALF_DEPTH
        if bp_y < leg_line:
            return LBWOutput(
                timestamp=datetime.now().isoformat(),
                final_decision="Not Out",
                decision_reason="Ball pitched outside leg stump",
                visual_decision=VisualDecision(
                    highlight_path=False,
                    highlight_miss_zone=True,
                    decision_overlay_color="green"
                )
            )

    # Determine which type of input we're dealing with
    
    # Type 2: Simple decision with just decision and reason
    if input_data.reason is not None and input_data.decision is not None:
        return LBWOutput(
            timestamp=datetime.now().isoformat(),
            final_decision=input_data.decision,
            decision_reason=input_data.reason,
            visual_decision=VisualDecision(
                highlight_path=False,
                highlight_miss_zone=input_data.decision.upper() == "NOT OUT",
                decision_overlay_color="green" if input_data.decision.upper() == "NOT OUT" else "red"
            )
        )
    
    # Type 3: Bat edge detection
    if input_data.bat_edge_detected is not None and input_data.bat_edge_detected:
        trajectory_path = input_data.ball_trajectory if input_data.ball_trajectory else []
        
        # Create trajectory summary if we have trajectory data
        trajectory_summary = None
        if trajectory_path:
            trajectory_summary = TrajectorySummary(
                initial_point=trajectory_path[0].dict(),
                final_point=trajectory_path[-1].dict(),
                closest_to_stumps=input_data.stump_coordinates.dict() if input_data.stump_coordinates else STUMP_CENTER.dict(),
                stump_hit_prediction=False  # Bat edge means not out, so no stump hit
            )
            
        return LBWOutput(
            timestamp=datetime.now().isoformat(),
            final_decision="Not Out",
            decision_reason="Bat edge detected",
            trajectory_summary=trajectory_summary,
            visual_decision=VisualDecision(
                highlight_path=True,
                highlight_miss_zone=False,
                decision_overlay_color="green"
            ),
            bat_edge_detected=True,
            confidence=1.0  # High confidence for bat edge detection
        )
    
    # Type 1: Trajectory-based input
    # Get the trajectory path from whichever field it's in
    trajectory_path = None
    if input_data.predicted_trajectory:
        trajectory_path = input_data.predicted_trajectory
    elif input_data.predicted_path:
        trajectory_path = input_data.predicted_path
    elif input_data.ball_trajectory:
        trajectory_path = input_data.ball_trajectory
    
    if not trajectory_path:
        raise ValueError("No trajectory data found in input")
    
    # If the input already has a decision, use it
    if input_data.decision:
        will_hit, overlap_percentage = False, 0.0
        if input_data.decision.upper() == "OUT":
            will_hit, overlap_percentage = True, 100.0
    else:
        # Otherwise, calculate if the ball will hit the stumps
        will_hit, overlap_percentage = _will_hit_stumps(trajectory_path)
    
    # Determine swing characteristics
    swing_type, swing_angle = "none", 0.0
    if input_data.swing_characteristics:
        swing_type = input_data.swing_characteristics.direction
        swing_angle = input_data.swing_characteristics.lateral_movement * 10.0
    elif input_data.swing_type:
        swing_type, swing_angle = _analyse_swing(trajectory_path)
    
    # Create the decision reason
    if will_hit:
        decision_reason = f"Ball projected to hit the stumps ({overlap_percentage:.1f}% overlap)"
        if swing_type != "none":
            decision_reason += f" with {swing_type} ({swing_angle:.1f}°)"
        else:
            decision_reason += " no significant swing"
    else:
        decision_reason = "Ball missing the stumps"
        if swing_type != "none":
            decision_reason += f" with {swing_type} ({swing_angle:.1f}°)"
    
    # Create the trajectory summary
    trajectory_summary = TrajectorySummary(
        initial_point=trajectory_path[0].dict(),
        final_point=trajectory_path[-1].dict(),
        closest_to_stumps=STUMP_CENTER.dict(),
        stump_hit_prediction=will_hit
    )
    
    # Create the visual decision
    visual_decision = VisualDecision(
        highlight_path=True,
        highlight_miss_zone=not will_hit,
        decision_overlay_color="red" if will_hit else "green"
    )
    
    # Create the output
    return LBWOutput(
        timestamp=datetime.now().isoformat(),
        final_decision="Out" if will_hit else "Not Out",
        decision_reason=decision_reason,
        trajectory_summary=trajectory_summary,
        visual_decision=visual_decision,
        confidence=input_data.confidence if input_data.confidence else (overlap_percentage / 100.0 if will_hit else 0.0)
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

