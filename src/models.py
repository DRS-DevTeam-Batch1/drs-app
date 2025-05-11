from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class Point3D(BaseModel):
    x: float
    y: float
    z: float

class TrajectoryPoint(Point3D):
    t: float

class SwingCharacteristics(BaseModel):
    direction: str
    lateral_movement: float
    rate: float

class BatEdgeDetection(BaseModel):
    bat_edge_detected: bool
    contact_time: Optional[float] = None
    contact_distance: Optional[float] = None

class SimpleDecision(BaseModel):
    decision: str
    reason: str

# Type 1 input
class TrajectoryInput(BaseModel):
    bounce_point: Optional[Point3D] = None
    confidence: float
    decision: str
    impact_location: Point3D
    predicted_trajectory: List[TrajectoryPoint]
    swing_characteristics: SwingCharacteristics

# Type 2 input
# Using SimpleDecision directly

# Type 3 input
class BatEdgeInput(BaseModel):
    bat_edge_detected: bool
    contact_time: float
    contact_distance: float
    ball_trajectory: List[TrajectoryPoint]
    bat_position: Point3D
    batsman_leg_position: Point3D
    stump_coordinates: Point3D

# Combined input model that can handle all three types
class LBWInput(BaseModel):
    # Common fields that might be present in any type
    predicted_path: Optional[List[TrajectoryPoint]] = None
    predicted_trajectory: Optional[List[TrajectoryPoint]] = None
    ball_trajectory: Optional[List[TrajectoryPoint]] = None
    impact_location: Optional[Point3D] = None
    bounce_point: Optional[Point3D] = None
    swing_type: Optional[str] = None
    
    # Type 1 specific fields
    confidence: Optional[float] = None
    decision: Optional[str] = None
    swing_characteristics: Optional[SwingCharacteristics] = None
    
    # Type 2 specific fields
    reason: Optional[str] = None
    
    # Type 3 specific fields
    bat_edge_detected: Optional[bool] = None
    contact_time: Optional[float] = None
    contact_distance: Optional[float] = None
    bat_position: Optional[Point3D] = None
    batsman_leg_position: Optional[Point3D] = None
    stump_coordinates: Optional[Point3D] = None

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
    trajectory_summary: Optional[TrajectorySummary] = None
    visual_decision: VisualDecision
    bat_edge_detected: Optional[bool] = None
    confidence: Optional[float] = None

class SwingAnalysisOutput(BaseModel):
    swing_type: str
    swing_degree: float
    predicted_deviation: float
    impact_analysis: dict
    is_dangerous_delivery: bool
    recommended_shot: str