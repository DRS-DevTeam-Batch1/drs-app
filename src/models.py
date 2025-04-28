from typing import List, Optional
from pydantic import BaseModel

class Point3D(BaseModel):
    x: float
    y: float
    z: float

class TrajectoryPoint(Point3D):
    t: float

class EdgeDetection(BaseModel):
    batEdgeDetected: bool
    contactFrame: Optional[int] = None
    contactZone: Optional[str] = None

class LBWInput(BaseModel):
    timestamp: str
    ball_trajectory: List[TrajectoryPoint]
    bounce_point: Point3D
    impact_point: Point3D
    bat_position: Point3D
    batsman_leg_position: Point3D
    stump_coordinates: List[Point3D]
    edge_detection: EdgeDetection

class BallContact(BaseModel):
    with_bat: bool
    with_leg: bool
    edge_detected: bool

class TrajectorySummary(BaseModel):
    initial_point: dict
    final_point: dict
    closest_to_stumps: dict
    stump_hit_prediction: bool

class VisualDecision(BaseModel):
    highlight_path: bool
    highlight_miss_zone: bool
    decision_overlay_color: str

class LBWOutput(BaseModel):
    timestamp: str
    final_decision: str
    decision_reason: str
    trajectory_summary: TrajectorySummary
    ball_contact: BallContact
    visual_decision: VisualDecision