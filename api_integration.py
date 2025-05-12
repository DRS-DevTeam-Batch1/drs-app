import requests
import json
import os
import time
from flask import Flask, request, jsonify, send_file
from overlay_module import CricketDRSOverlay, process_from_json_file
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Configuration for module APIs
MODULE_CONFIGS = [
    {
        "name": "Mobile UI (Camera Module)",
        "url": "https://api.example.com/mobile_ui",
        "output_file": "mobile_ui_data.json",
        "enabled": False  # Set to True when API is available
    },
    {
        "name": "Ball and Object Tracking Module",
        "url": "https://api.example.com/ball_object_tracking",
        "output_file": "ball_object_tracking_data.json",
        "enabled": False
    },
    {
        "name": "Bat's Edge Detection Module",
        "url": "https://api.example.com/bats_edge_detection",
        "output_file": "bats_edge_detection_data.json",
        "enabled": False
    },
    {
        "name": "Trajectory Analysis Module",
        "url": "https://api.example.com/trajectory_analysis",
        "output_file": "trajectory_analysis_data.json",
        "enabled": False
    },
    {
        "name": "Decision Making Module",
        "url": "https://api.example.com/decision_making",
        "output_file": "decision_making_data.json",
        "enabled": False
    }
]

# Default paths
DEFAULT_TRAJECTORY_DATA = "trajectory_data.json"
DEFAULT_VIDEO_INPUT = "input_cricket_video.mp4"
DEFAULT_VIDEO_OUTPUT = "output_drs_video.mp4"


def fetch_module_data():
    """Fetch data from all enabled module APIs and save to their respective files"""
    results = {}
    
    for module in MODULE_CONFIGS:
        if not module["enabled"]:
            logger.info(f"Skipping disabled module: {module['name']}")
            continue
        
        try:
            logger.info(f"Fetching data from {module['name']} at {module['url']}")
            response = requests.get(module["url"], timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Save to file
            with open(module["output_file"], 'w') as f:
                json.dump(data, f, indent=4)
                
            logger.info(f"Successfully saved data to {module['output_file']}")
            results[module["name"]] = "Success"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from {module['name']}: {str(e)}")
            results[module["name"]] = f"Error: {str(e)}"
    
    return results


def merge_module_data():
    """Combine all module data files into one without special formatting"""
    merged_data = {}
    
    for module in MODULE_CONFIGS:
        if not module["enabled"]:
            continue
            
        output_file = module["output_file"]
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    module_data = json.load(f)
                    # Use module name as key in merged data
                    merged_data[module["name"]] = module_data
            except Exception as e:
                logger.error(f"Error reading {output_file}: {str(e)}")
                continue
    
    # If we got data from any module, save it
    if merged_data:
        merged_file = "merged_data.json"
        with open(merged_file, 'w') as f:
            json.dump(merged_data, f)
        logger.info(f"Combined data saved to {merged_file}")
        return merged_file
    
    # Fall back to default if no modules provided data
    logger.info("No module data available, using default trajectory data")
    return DEFAULT_TRAJECTORY_DATA


# API Routes
@app.route('/api/fetch-module-data', methods=['POST'])
def api_fetch_module_data():
    """API endpoint to trigger fetching data from all modules"""
    results = fetch_module_data()
    return jsonify({"status": "completed", "results": results})


@app.route('/api/process-video', methods=['POST'])
def api_process_video():
    """API endpoint to process video with trajectory data"""
    data = request.json or {}
    
    video_path = data.get('video_path', DEFAULT_VIDEO_INPUT)
    output_path = data.get('output_path', DEFAULT_VIDEO_OUTPUT)
    
    # If merge_data is true, merge data from all modules
    # Otherwise use the specified trajectory_data or default
    if data.get('merge_data', False):
        trajectory_data_path = merge_module_data()
    else:
        trajectory_data_path = data.get('trajectory_data', DEFAULT_TRAJECTORY_DATA)
    
    try:
        logger.info(f"Processing video: {video_path} with trajectory data: {trajectory_data_path}")
        result_path = process_from_json_file(video_path, trajectory_data_path, output_path)
        return jsonify({
            "status": "success", 
            "output_path": result_path,
            "message": f"Video processing complete. Output saved to: {result_path}"
        })
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/output-video', methods=['GET'])
def api_get_output_video():
    """API endpoint to download the processed video"""
    output_path = request.args.get('path', DEFAULT_VIDEO_OUTPUT)
    
    if not os.path.exists(output_path):
        return jsonify({"status": "error", "message": "Output video not found"}), 404
    
    return send_file(output_path, as_attachment=True)


@app.route('/api/status', methods=['GET'])
def api_status():
    """API endpoint to check the status of the service"""
    # Check if default trajectory data exists
    trajectory_exists = os.path.exists(DEFAULT_TRAJECTORY_DATA)
    
    # Get enabled modules
    enabled_modules = [m["name"] for m in MODULE_CONFIGS if m["enabled"]]
    
    return jsonify({
        "status": "online",
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "trajectory_data_available": trajectory_exists,
        "enabled_modules": enabled_modules,
        "disabled_modules": [m["name"] for m in MODULE_CONFIGS if not m["enabled"]]
    })


if __name__ == "__main__":
    # Run the Flask app
    logger.info("Starting Cricket DRS Overlay API server")
    app.run(host='0.0.0.0', port=8000, debug=False)
