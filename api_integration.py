import requests
import json
import os
import time
import base64
from flask import Flask, request, jsonify, send_file
from overlay_module import process_from_json_file
import logging
import cv2

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
        "name": "Ball and Object Tracking Module",
        "url": "https://api.example.com/ball_object_tracking",
        "output_file": "ball_object_tracking_data.json",
        "enabled": False  # Set to True to enable
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


def convert_video_to_json(video_path):
    """Convert a video to base64-encoded JSON frames"""
    try:
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            raise Exception(f"Could not open video file: {video_path}")

        frames = []
        frame_id = 0

        while True:
            success, frame = video.read()
            if not success:
                break

            frame_id += 1
            timestamp = format_timestamp(video.get(cv2.CAP_PROP_POS_MSEC))

            # Convert frame to base64
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            frames.append({
                "frame_id": frame_id,
                "timestamp": timestamp,
                "image_data": img_base64,
                "metadata": {
                    "camera_id": "cam_1"
                }
            })

        video.release()

        # Save to file
        output_file = f"{os.path.splitext(video_path)[0]}_frames.json"
        with open(output_file, 'w') as f:
            json.dump(frames, f)

        logger.info(f"Video converted to JSON: {output_file}")
        return output_file

    except Exception as e:
        logger.error(f"Error converting video to JSON: {str(e)}")
        raise


def format_timestamp(milliseconds):
    """Format milliseconds to HH:MM:SS.mmm format"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def process_through_modules(data):
    """Process data sequentially through all enabled modules"""
    current_data = data
    enabled_modules = [module for module in MODULE_CONFIGS if module["enabled"]]

    for i, module in enumerate(enabled_modules):
        try:
            logger.info(f"Processing module {i + 1}/{len(enabled_modules)}: {module['name']} at {module['url']}")

            # Send the current data directly to the module
            response = requests.post(module["url"], json=current_data, timeout=30)
            response.raise_for_status()

            # Update current data with response from this module
            current_data = response.json()

            # Save individual module output for later merging
            with open(module["output_file"], 'w') as f:
                json.dump(current_data, f, indent=4)

            logger.info(f"Successfully saved data to {module['output_file']}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error processing through {module['name']}: {str(e)}")
            break

    return current_data


def merge_module_data():
    """Properly merge all module data files into a single valid JSON structure"""
    merged_data = {}

    for module in MODULE_CONFIGS:
        if not module["enabled"]:
            continue

        output_file = module["output_file"]
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    module_data = json.load(f)
                    if isinstance(module_data, dict):
                        merged_data.update(module_data)
                    elif isinstance(module_data, list):
                        # If we already have a list, extend it
                        if not merged_data:
                            merged_data = module_data
                        elif isinstance(merged_data, list):
                            merged_data.extend(module_data)
                        else:
                            # Convert to list if needed
                            merged_data = [merged_data, module_data]

                    logger.info(f"Merged data from {output_file}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {output_file}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Error reading {output_file}: {str(e)}")
                continue

    # If we got data from any module, save it
    if merged_data:
        merged_file = "merged_data.json"
        with open(merged_file, 'w') as f:
            json.dump(merged_data, f, indent=4)
        logger.info(f"Combined data saved to {merged_file}")
        return merged_file

    # Fall back to default if no modules provided data
    logger.info("No module data available, using default trajectory data")
    return DEFAULT_TRAJECTORY_DATA


# API Routes
@app.route('/api/process', methods=['POST'])
def api_process():
    """API endpoint to process JSON data received in the request through modules"""
    try:
        # Get JSON data from the request payload
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided in request"}), 400

        # Save initial data for reference
        with open("initial_data.json", 'w') as f:
            json.dump(data, f, indent=4)

        # Process through all modules
        process_through_modules(data)

        # Merge all module data
        merged_data_path = merge_module_data()

        # Process the merged data with the overlay module
        output_path = DEFAULT_VIDEO_OUTPUT
        logger.info(f"Processing with merged data: {merged_data_path}")
        result_path = process_from_json_file(None, merged_data_path, output_path)

        # Return the video file directly
        return send_file(result_path, mimetype='video/mp4', as_attachment=True)

    except Exception as e:
        logger.error(f"Error in processing pipeline: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/convert-video', methods=['POST'])
def api_convert_video():
    """API endpoint to convert video path from request to JSON and process through modules"""
    try:
        data = request.json
        if not data or 'video_path' not in data:
            return jsonify({"status": "error", "message": "Missing video_path parameter"}), 400

        video_path = data['video_path']
        if not os.path.exists(video_path):
            return jsonify({"status": "error", "message": f"Video file not found: {video_path}"}), 404

        # Convert video to JSON frames
        json_file = convert_video_to_json(video_path)

        # Load the JSON data
        with open(json_file, 'r') as f:
            video_data = json.load(f)

        # Process through all modules
        process_through_modules(video_data)

        # Merge all module data
        merged_data_path = merge_module_data()

        # Process the merged data with the overlay module
        output_path = DEFAULT_VIDEO_OUTPUT
        logger.info(f"Processing with merged data: {merged_data_path}")
        result_path = process_from_json_file(video_path, merged_data_path, output_path)

        # Return the video file directly
        return send_file(result_path, mimetype='video/mp4', as_attachment=True)

    except Exception as e:
        logger.error(f"Error converting and processing video: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    # Run the Flask app
    logger.info("Starting Cricket DRS Overlay API server")
    app.run(host='0.0.0.0', port=8000, debug=False)