from typing import List
from pydantic import BaseModel

class Point3D(BaseModel):
    x: float
    y: float
    z: float

class TrajectoryPoint(Point3D):
    t: float

class LBWInput(BaseModel):
    predicted_path: List[TrajectoryPoint]
    impact_location: Point3D
    bounce_point: Point3D
    swing_type: str

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
    decision_confidence: float  
    umpires_call_flag: bool     
    trajectory_summary: TrajectorySummary
    visual_decision: VisualDecision


class SwingAnalysisOutput(BaseModel):
    swing_type: str
    swing_degree: float
    predicted_deviation: float
    impact_analysis: dict
    is_dangerous_delivery: bool
    recommended_shot: str