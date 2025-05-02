from flask import Flask, request, jsonify
import math

app = Flask(_name_)

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