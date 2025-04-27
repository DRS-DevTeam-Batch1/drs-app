import json
from src.models import LBWInput, LBWOutput, BallContact, TrajectorySummary, VisualDecision, Point3D

def is_stump_hit(trajectory, stump_coordinates):
    final_point = trajectory[-1]
    for stump in stump_coordinates:
        distance = ((final_point.x - stump.x) ** 2 +
                    (final_point.y - stump.y) ** 2 +
                    (final_point.z - stump.z) ** 2) ** 0.5
        if distance < 0.15:
            return True, stump
    return False, stump_coordinates[0] if stump_coordinates else Point3D(x=0.0, y=0.0, z=0.0)

def detect_lbw(trajectory, batsman_leg_position, stump_coordinates):
    if not trajectory or not batsman_leg_position or not stump_coordinates:
        return False
    return True

def process_decision(input_data: LBWInput) -> LBWOutput:
    stump_hit, closest_stump = is_stump_hit(input_data.ball_trajectory, input_data.stump_coordinates)
    
    ball_contact = BallContact(
        with_bat=input_data.edge_detection.batEdgeDetected,
        with_leg=True,
        edge_detected=False
    )
    
    if ball_contact.with_bat:
        final_decision = "Edge Detected"
        decision_reason = "Bat edge detected before impact"
    elif detect_lbw(input_data.ball_trajectory, input_data.batsman_leg_position, input_data.stump_coordinates):
        if stump_hit:
            final_decision = "Out"
            decision_reason = "Ball hitting the stumps (LBW)"
        else:
            final_decision = "Not Out"
            decision_reason = "Ball missing the stumps"
    else:
        final_decision = "Not Out"
        decision_reason = "Impact or pitch conditions not met"
    
    trajectory_summary = TrajectorySummary(
        initial_point=input_data.ball_trajectory[0].model_dump() if input_data.ball_trajectory else {},
        final_point=input_data.ball_trajectory[-1].model_dump() if input_data.ball_trajectory else {},
        closest_to_stumps=closest_stump.model_dump(),
        stump_hit_prediction=stump_hit
    )
    
    visual_decision = VisualDecision(
        highlight_path=True,
        highlight_miss_zone=not stump_hit,
        decision_overlay_color="red" if final_decision == "Out" else "green"
    )
    
    return LBWOutput(
        timestamp=input_data.timestamp,
        final_decision=final_decision,
        decision_reason=decision_reason,
        trajectory_summary=trajectory_summary,
        ball_contact=ball_contact,
        visual_decision=visual_decision
    )

def main():
    with open("data/sample_input_lbw.json") as f:
        input_json = json.load(f)
    
    input_data = LBWInput.model_validate(input_json)
    result = process_decision(input_data)
    
    with open("data/sample_output.json", "w") as f:
        json.dump(result.model_dump(), f, indent=4)
    
    print("Decision:", result.final_decision)

if __name__ == "__main__":
    main()
