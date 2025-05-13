from flask import Flask, request, jsonify
import json
import os
from trajectory_analysis import TrajectoryAnalysisWithML, predict_trajectory
import requests

app = Flask(__name__)
_port = 6051

#currently set path to decision. change if ports are changed.
DECISION_API_URL = os.getenv("DECISION_API_URL", "http://0.0.0.0:8001/api/lbw-decision")

@app.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy", "module": "trajectory-analysis"}), 200

@app.route("/analyze_trajectory", methods=["POST"])
def analyze_trajectory():
    """
    API endpoint to analyze ball trajectory for LBW decisions.
    This endpoint is called by the bat-edge-detection module when:
    1. No bat edge is detected
    2. Ball hits batsman's leg
    
    Expected input format:
    {
        "bat_edge_detected": false,  # Must be false to proceed
        "ball_trajectory": [
            {"x": float, "y": float, "z": float, "t": float},
            ...
        ],
        "bat_position": {"x": float, "y": float, "z": float},
        "batsman_leg_position": {"x": float, "y": float, "z": float},
        "stump_coordinates": {"x": float, "y": float, "z": float}
        optional additional parameters like contact_time, etc.
    }
    
    Returns:
    {
        "decision": "OUT" or "NOT OUT",
        "confidence": float,  # Confidence score between 0 and 1
        "predicted_trajectory": [
            {"x": float, "y": float, "z": float, "t": float},
            ...
        ],
        "impact_location": {"x": float, "y": float, "z": float},
        "bounce_point": {"x": float, "y": float, "z": float} or null,
        "swing_characteristics": {
            "lateral_movement": float,
            "direction": string,
            "rate": float,
            "type": string
        }
    }
    """
    try:
        # Extract data from request
        data = request.get_json()
        
        # Validate input
        if data is None:
            return jsonify({"error": "No data provided"}), 400
        
        # If bat edge was detected, no need for trajectory analysis
        if data.get("bat_edge_detected", True):
            return jsonify({
                "decision": "NOT OUT",
                "reason": "Bat edge detected"
            }), 200
        
        # Extract required fields
        ball_trajectory = data.get("ball_trajectory")
        bat_position = data.get("bat_position")
        batsman_leg_position = data.get("batsman_leg_position")
        stump_coordinates = data.get("stump_coordinates")
        
        # Validate required fields
        if not all([ball_trajectory, bat_position, batsman_leg_position, stump_coordinates]):
            missing_fields = []
            if not ball_trajectory: missing_fields.append("ball_trajectory")
            if not bat_position: missing_fields.append("bat_position")
            if not batsman_leg_position: missing_fields.append("batsman_leg_position")
            if not stump_coordinates: missing_fields.append("stump_coordinates")
            
            return jsonify({
                "error": "Missing required fields",
                "missing_fields": missing_fields
            }), 400
        
        # Use the trajectory analysis module
        model_path = os.environ.get("MODEL_PATH", "trajectory_model.pkl")
        results = predict_trajectory(
            ball_trajectory, 
            stump_coordinates, 
            bat_position, 
            batsman_leg_position,
            model_path=model_path
        )
        print("Trajectory prediction results:", results)
        
        # Call the next module (decision API)
        # Make sure their server is running first
        try:
            # Format the data according to what the decision API expects
            decision_api_data = {
                "predicted_path": results.get("predicted_trajectory", []),
                "impact_location": results.get("impact_location", {}),
                "bounce_point": results.get("bounce_point", {}),
                "swing_type": results.get("swing_characteristics", {}).get("type", "conventional swing")
            }
            
            print("Sending to decision API:", json.dumps(decision_api_data, indent=2))
            
            decision_response = requests.post(
                DECISION_API_URL,
                json=decision_api_data
            )
            
            # Check if the request was successful
            if decision_response.status_code == 200:
                # Parse the JSON content from the response
                decision_result = decision_response.json()
                print("Decision API response:", decision_result)
                
                # Return the decision result directly instead of the trajectory results
                return jsonify(decision_result), 200
            else:
                print(f"Decision API returned error: {decision_response.status_code}")
                print(f"Response content: {decision_response.text}")
                # Fall back to trajectory results if decision API fails
                return jsonify(results), 200
                
        except Exception as e:
            print(f"Error calling decision API: {str(e)}")
            # Fall back to trajectory results if decision API call fails
            return jsonify(results), 200
        
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/visualize_trajectory", methods=["POST"])
def visualize_trajectory():
    """
    Optional endpoint to generate a visualization of the trajectory
    """
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({"error": "No data provided"}), 400
        
        ball_trajectory = data.get("ball_trajectory")
        if not ball_trajectory:
            return jsonify({"error": "Missing ball_trajectory field"}), 400
        
        # Create a visualization (this would need to be implemented)
        analyzer = TrajectoryAnalysisWithML()
        visualization_path = f"visualization_{request.id}.png"
        analyzer.visualize_trajectory(ball_trajectory, save_path=visualization_path)
        
        # In a real implementation, you might return the image or a URL to it
        return jsonify({
            "status": "success",
            "visualization_path": visualization_path
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error generating visualization: {str(e)}")
        return jsonify({"error": str(e)}), 500

# For testing the API independently of input, i.e just for our output
@app.route("/test", methods=["GET"])
def test_endpoint():
    """
    Test endpoint with sample data
    """
    # Example data for test end point
    ball_path = [
        {"x": 0.1, "y": 1.8, "z": 0.0, "t": 0.0},
        {"x": 0.15, "y": 1.7, "z": 2.0, "t": 0.1},
        {"x": 0.2, "y": 1.5, "z": 4.0, "t": 0.2},  
        {"x": 0.25, "y": 1.2, "z": 6.0, "t": 0.3},
        {"x": 0.3, "y": 0.8, "z": 8.0, "t": 0.4},
        {"x": 0.35, "y": 0.5, "z": 10.0, "t": 0.5},
        {"x": 0.4, "y": 0.7, "z": 12.0, "t": 0.6},
        {"x": 0.45, "y": 0.9, "z": 14.0, "t": 0.7}
    ]
    
    stump_position = {"x": 0.7, "y": 0.0, "z": 20.0}
    bat_position = {"x": 0.6, "y": 0.8, "z": 16.0}
    leg_position = {"x": 0.5, "y": 0.9, "z": 15.0}
    
    # Run the integrated analysis
    results = predict_trajectory(
        ball_path, stump_position, bat_position, leg_position,
        model_path="trajectory_model.pkl"
    )
    
    # Test the decision API as well
    try:
        # Format the data according to what the decision API expects
        decision_api_data = {
            "trajectory_summary": {
                "initial_point": ball_path[0] if ball_path else {"x": 0, "y": 0, "z": 0, "t": 0},
                "final_point": ball_path[-1] if ball_path else {"x": 0, "y": 0, "z": 0, "t": 0},
                "closest_to_stumps": {
                    "x": results.get("impact_location", {}).get("x", 0),
                    "y": results.get("impact_location", {}).get("y", 0),
                    "z": results.get("impact_location", {}).get("z", 0)
                },
                "stump_hit_prediction": results.get("decision") == "OUT"
            },
            "bat_edge_detected": None,
            "confidence": results.get("confidence", 0.0)
        }
        
        print("Test - Sending to decision API:", json.dumps(decision_api_data, indent=2))
        
        decision_response = requests.post(
            DECISION_API_URL,
            json=decision_api_data
        )
        
        if decision_response.status_code == 200:
            decision_result = decision_response.json()
            print("Test decision API response:", decision_result)
            return jsonify(decision_result), 200
        else:
            print(f"Test decision API error: {decision_response.status_code}")
            print(f"Response content: {decision_response.text}")
            return jsonify(results), 200
    except Exception as e:
        print(f"Error calling test decision API: {str(e)}")
        return jsonify(results), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", _port))
    app.run(host="0.0.0.0", port=port, debug=True)