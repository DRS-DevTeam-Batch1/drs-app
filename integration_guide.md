# API Integration Guide for Interation Team

This guide explains how to use the REST API integration for the Cricket DRS (Decision Review System) Overlay Module.


## Files Structure

- `overlay_module.py` - Core video processing and overlay logic
- `api_integration.py` - Flask server that provides REST API endpoints
- `trajectory_data.json` - Dummy trajectory data (used when other modules' APIs are offline)
- `input_cricket_video.mp4` - Sample input video
- `output_drs_video.mp4` - Processed output video

## Getting Started

### Prerequisites

Install the required dependencies:

```bash
pip install flask requests
```

### Running the API Server

Start the API server:

```bash
python api_integration.py
```

This will start the server at http://localhost:5000 by default.

## API Endpoints

### Check API Status

```
GET /api/status
```

Returns the current status of the API server, including which modules are enabled.

### Fetch Module Data

```
POST /api/fetch-module-data
```

Triggers fetching data from all enabled module APIs and saves it to their respective files.

### Process Video

```
POST /api/process-video
```

Processes a video with trajectory data.

Parameters (JSON):
- `video_path` (optional): Path to input video (default: "input_cricket_video.mp4")
- `trajectory_data` (optional): Path to trajectory data file (default: "trajectory_data.json")
- `output_path` (optional): Path for output video (default: "output_drs_video.mp4")
- `merge_data` (optional): If true, merge data from all modules (default: false)

### Get Output Video

```
GET /api/output-video?path={output_path}
```

Downloads the processed output video.

Parameters (query string):
- `path` (optional): Path to the output video (default: "output_drs_video.mp4")

## Integration with Other Modules

The system is designed to integrate with the following modules:

1. Mobile UI (Camera Module)
2. Ball and Object Tracking Module
3. Bat's Edge Detection Module
4. Trajectory Analysis Module
5. Decision Making Module

Currently, these module APIs are configured as disabled since they are not yet online. When they become available:

1. Update the `MODULE_CONFIGS` in `api_integration.py` to set `enabled: True` for the available modules
2. Update the URLs to point to the actual API endpoints

## Development Notes

### Using Dummy Data

While the other modules' APIs are offline, the system will continue using the dummy `trajectory_data.json`. The `merge_module_data()` function in `api_integration.py` is a placeholder for the actual merging logic that would combine data from multiple modules.

### Integration Team Instructions

For the integration team:

1. Make API calls to the endpoints described above
2. The main workflow is:
   - First call `/api/fetch-module-data` to get data from all modules
   - Then call `/api/process-video` to generate the output video
   - Finally use `/api/output-video` to download the result


