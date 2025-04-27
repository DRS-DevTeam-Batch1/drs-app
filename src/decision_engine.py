import json
import os

def parse_input(input_data):
    """Parse the input data."""
    return {
        "trajectory": input_data.get("ball_trajectory", []),
        "bat_position": input_data.get("bat_position", {}),
        "batsman_leg_position": input_data.get("batsman_leg_position", {}),
        "stump_coordinates": input_data.get("stump_coordinates", []),
        "ball_contact_with_bat": input_data.get("ball_contact_with_bat", False),
        "edge_detection": input_data.get("edge_detection", {})
    }

def is_stump_hit(trajectory, stump_coordinates):
    """Check if ball will hit any stump."""
    final_point = trajectory[-1]
    for stump in stump_coordinates:
        distance = ((final_point["x"] - stump["x"]) ** 2 +
                    (final_point["y"] - stump["y"]) ** 2 +
                    (final_point["z"] - stump["z"]) ** 2) ** 0.5
        if distance < 0.15:  # threshold distance
            return True, stump
    return False, stump_coordinates[0] if stump_coordinates else {}

def detect_lbw(trajectory, batsman_leg_position, stump_coordinates):
    """Simple LBW detection mock."""
    if not trajectory or not batsman_leg_position or not stump_coordinates:
        return False
    return True

def generate_output(input_data):
    trajectory = input_data["trajectory"]
    stump_hit, closest_stump = is_stump_hit(trajectory, input_data["stump_coordinates"])

    ball_contact = {
        "with_bat": input_data.get("edge_detection", {}).get("batEdgeDetected", False),
        "with_leg": True,
        "edge_detected": input_data.get("edge_detection", {}).get("batEdgeDetected", False)
    }

    if ball_contact["with_bat"]:
        final_decision = "Edge Detected"
        decision_reason = "Bat edge detected before impact"
    elif detect_lbw(trajectory, input_data["batsman_leg_position"], input_data["stump_coordinates"]):
        if stump_hit:
            final_decision = "Out"
            decision_reason = "Ball hitting the stumps (LBW)"
        else:
            final_decision = "Not Out"
            decision_reason = "Ball missing the stumps"
    else:
        final_decision = "Not Out"
        decision_reason = "Impact or pitch conditions not met"

    return {
        "timestamp": input_data.get("timestamp"),
        "final_decision": final_decision,
        "decision_reason": decision_reason,
        "impact_point": input_data.get("impact_point"),
        "trajectory_summary": {
            "initial_point": trajectory[0] if trajectory else {},
            "final_point": trajectory[-1] if trajectory else {},
            "closest_to_stumps": closest_stump,
            "stump_hit_prediction": stump_hit
        },
        "ball_contact": ball_contact,
        "visual_decision": {
            "highlight_path": True,
            "highlight_impact": True,
            "highlight_miss_zone": not stump_hit,
            "decision_overlay_color": "red" if final_decision == "Out" else "green"
        }
    }

def main(input_filepath):
    with open(input_filepath) as f:
        input_data = json.load(f)

    parsed = parse_input(input_data)
    result = generate_output(parsed)

    # Generate corresponding output filename
    output_filepath = input_filepath.replace(".json", "_output.json")
    with open(output_filepath, "w") as f:
        json.dump(result, f, indent=4)
    
    print(f"✅ Processed {input_filepath}")
    print("Decision:", result["final_decision"])

if __name__ == "__main__":
    main("data/sample_input_lbw_out.json")
    main("data/sample_input_lbw_not_out.json")