import json

def parse_input(input_data):
    """Parse the input data."""
    return {
        "trajectory": input_data.get("ball_trajectory", []),
        "bat_position": input_data.get("bat_position", {}),
        "batsman_leg_position": input_data.get("batsman_leg_position", {}),
        "stump_coordinates": input_data.get("stump_coordinates", []),
        "ball_contact_with_bat": input_data.get("ball_contact_with_bat", False)
    }

def is_stump_hit(trajectory, stump_coordinates):
    """Check if the ball would hit any stump."""
    final_point = trajectory[-1]
    for stump in stump_coordinates:
        distance = ((final_point["x"] - stump["x"]) ** 2 +
                    (final_point["y"] - stump["y"]) ** 2 +
                    (final_point["z"] - stump["z"]) ** 2) ** 0.5
        if distance < 0.15:  # threshold distance to consider it hitting stump
            return True, stump
    return False, stump_coordinates[0] if stump_coordinates else {}

def detect_lbw(trajectory, batsman_leg_position, stump_coordinates):
    """Assume the conditions are valid for LBW detection."""
    if not trajectory or not batsman_leg_position or not stump_coordinates:
        return False
    return True  # Assuming the conditions are valid for mock purposes

def generate_output(input_data):
    trajectory = input_data["ball_trajectory"]
    stump_hit, closest_stump = is_stump_hit(trajectory, input_data["stump_coordinates"])

    ball_contact = {
        "with_bat": input_data["ball_contact_with_bat"],  # This comes from Module 3
        "with_leg": True,   # Assume it hit the leg 
        "edge_detected": False  
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
        "trajectory_summary": {
            "initial_point": trajectory[0] if trajectory else {},
            "final_point": trajectory[-1] if trajectory else {},
            "closest_to_stumps": closest_stump,
            "stump_hit_prediction": stump_hit
        },
        "ball_contact": ball_contact,
        "visual_decision": {
            "highlight_path": True,
            "highlight_miss_zone": not stump_hit,
            "decision_overlay_color": "red" if final_decision == "Out" else "green"
        }
    }

def main():
    with open("data/sample_input_lbw.json") as f:
        input_data = json.load(f)

    parsed = parse_input(input_data)
    result = generate_output(parsed)

    with open("data/sample_output.json", "w") as f:
        json.dump(result, f, indent=4)
    
    print("Decision:", result["final_decision"])

if __name__ == "__main__":
    main()