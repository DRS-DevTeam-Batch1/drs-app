from flask import Flask, request, jsonify
import math
import requests

app = Flask(__name__)

def euclidean_distance(p1, p2):
    return math.sqrt(
        (p1["x"] - p2["x"]) ** 2 +
        (p1["y"] - p2["y"]) ** 2 +
        (p1["z"] - p2["z"]) ** 2
    )

def detect_bat_edge(ball_trajectory, bat_position, threshold=0.05):
    for point in ball_trajectory:
        dist = euclidean_distance(point, bat_position)
        print(f"Time {point['t']:.2f}s → Ball-Bat Distance: {dist:.4f} m")
        if dist < threshold:
            return {
                "bat_edge_detected": True,
                "contact_time": point["t"],
                "contact_distance": dist
            }

    return {
        "bat_edge_detected": False,
        "contact_time": None,
        "contact_distance": None
    }

# @app.route("/detect_batedge", methods=["POST"])
# def handle_batedge():
#     try:
#         data = request.get_json()

#         # Extract required fields
#         ball_trajectory = data["ball_trajectory"]
#         bat_position = data["bat_position"]
#         batsman_leg = data.get("batsman_leg_position")
#         stump_coords = data.get("stump_coordinates")

#         detection = detect_bat_edge(ball_trajectory, bat_position)
#         output_payload = {
#             # "bat_edge_detected": detection["bat_edge_detected"],
#             # "contact_time": detection["contact_time"],
#             # "contact_distance": detection["contact_distance"],
#             # "ball_trajectory": ball_trajectory if detection["bat_edge_detected"] else [],
#             # "bat_position": bat_position,
#             # "batsman_leg_position": batsman_leg,
#             # "stump_coordinates": stump_coords
#             "bat_edge_detected": detection, 
#             "ball_trajectory": ball_trajectory,  # ball_trajectory should be provided from detection
#             "bat_position": bat_position,
#             "batsman_leg_position": batsman_leg,
#             "stump_coordinates": stump_coords,
#         }

#         # Forwarding to another module (Updated the IP to the correct one)
#         trajectory_api = "http://192.168.18.50:6051/analyze_trajectory"

#         response = requests.post(trajectory_api, json=output_payload)
#         print("Forwarded to trajectory module. Response:", response.text)

#         return jsonify({
#             "status": "success",
#             "bat_edge_detected": detection["bat_edge_detected"],
#             "forwarded_to_trajectory": True,
#             "trajectory_module_response": response.json()
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route("/detect_batedge", methods=["POST"])
def handle_batedge():
    try:
        data = request.get_json()

        # Validate input
        required_fields = ["ball_trajectory", "bat_position", "batsman_leg_position", "stump_coordinates"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print("helloword")
            return jsonify({"error": "Missing required fields", "missing": missing_fields}), 400
        # Extract stump coordinates (handling a list if needed)
        stump_coords = data.get("stump_coordinates")

        # If stump_coordinates is a list, use the first element or adjust the logic based on your needs
        if isinstance(stump_coords, list):
            stump_coords = stump_coords[0]  # Pick the first entry, or adjust as needed

        # Now stump_coordinates should be a dictionary
        if not stump_coords:
            return jsonify({"error": "Missing or invalid stump_coordinates"}), 400

        ball_trajectory = data["ball_trajectory"]
        bat_position = data["bat_position"]
        batsman_leg = data["batsman_leg_position"]
        #stump_coords = data["stump_coordinates"]
        # Perform bat edge detection
        detection = detect_bat_edge(ball_trajectory, bat_position)

        # Case 1: Edge detected → Stop here
        if detection.get("bat_edge_detected", False):

            return jsonify({
                "status": "bat edge detected",
                "bat_edge_detected": True,
                "ball_trajectory": ball_trajectory,
                "contact_time": detection.get("contact_time"),
                "contact_distance": detection.get("contact_distance")
            }), 200

        # Case 2: No bat edge → forward to trajectory module
        output_payload = {
            "bat_edge_detected": False,
            "ball_trajectory": ball_trajectory,
            "bat_position": bat_position,
            "batsman_leg_position": batsman_leg,
            "stump_coordinates": stump_coords
        }
        print("Forwarding payload to trajectory module:", output_payload)

        # Forward to trajectory module
        trajectory_api = "http://192.168.18.50:6051/analyze_trajectory"
        response = requests.post(trajectory_api, json=output_payload)
        print("Forwarded to trajectory module. Response:", response.text)

        return jsonify({
            "status": "success",
            "bat_edge_detected": False,
            "forwarded_to_trajectory": True,
            "trajectory_module_response": response.json()
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
