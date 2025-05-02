@app.route("/detect_batedge", methods=["POST"])
def handle_batedge():
    try:
        data = request.get_json()

        # Extract required fields
        ball_trajectory = data["ball_trajectory"]
        bat_position = data["bat_position"]
        batsman_leg = data.get("batsman_leg_position")
        stump_coords = data.get("stump_coordinates")

        detection = detect_bat_edge(ball_trajectory, bat_position)

        output_payload = {
            "bat_edge_detected": detection["bat_edge_detected"],
            "contact_time": detection["contact_time"],
            "contact_distance": detection["contact_distance"],
            "ball_trajectory": ball_trajectory if detection["bat_edge_detected"] else None,
            "bat_position": bat_position,
            "batsman_leg_position": batsman_leg,
            "stump_coordinates": stump_coords
        }