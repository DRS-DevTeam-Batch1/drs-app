# DRS App Documentation

## Project Structure

- **`/dev_server.py`**: Entry point for running the FastAPI application in development mode with auto-reload.
- **`/server.py`**: Entry point for running the FastAPI application in production mode, allowing configuration through environment variables.
- **`/test_api.py`**: Script to test the API by sending a sample input and printing the response.
- **`/models.py`**: Contains Pydantic models that define the structure of input and output data for the API.
- **`/main.py`**: Main application file that sets up the FastAPI app, middleware, and API endpoints.
- **`/decision_engine.py`**: Contains the logic for processing the LBW decision based on the input data.
- **`/requirements.txt`**: Lists the dependencies required to run the project.

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a virtual environment (optional but recommended)**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages**:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode

To run the application in development mode with auto-reload, execute:

```bash
python dev_server.py
```

The application will be accessible at `http://127.0.0.1:8000`.

### Production Mode

To run the application in production mode, you can use:

```bash
python server.py
```

You can configure the host, port, and log level using environment variables:

- **HOST**: Default is `0.0.0.0`
- **PORT**: Default is `8000`
- **LOG_LEVEL**: Default is `info`

## API Endpoints

### POST `/api/lbw-decision`

- **Description**: Processes the LBW decision based on the provided input data.
- **Request Body**: Must conform to the `LBWInput` model defined in `models.py`.
- **Response**: Returns a JSON object conforming to the `LBWOutput` model.

#### Example Request

```json
{
  "predicted_path": [
    { "x": 2.0, "y": 0.8, "z": 0.3, "t": 0.1 },
    { "x": 1.8, "y": 0.6, "z": 0.2, "t": 0.1 }
  ],
  "impact_location": { "x": 1.6, "y": 0.4, "z": 0.1 },
  "bounce_point": { "x": 2.2, "y": 1.0, "z": 0.0 },
  "swing_type": "inswing"
}
```

#### Example Response

```json
{
  "decision_reason": "Ball projected to hit the stumps (100.0% overlap) no significant swing",
  "final_decision": "Out",
  "timestamp": "2025-05-03T06:44:00.961750",
  "trajectory_summary": {
    "closest_to_stumps": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.71
    },
    "final_point": {
      "t": 0.8,
      "x": 0.02,
      "y": 0.02,
      "z": 0.71
    },
    "initial_point": {
      "t": 0.0,
      "x": 0.3,
      "y": 1.5,
      "z": 1.0
    },
    "stump_hit_prediction": true
  },
  "visual_decision": {
    "decision_overlay_color": "red",
    "highlight_miss_zone": false,
    "highlight_path": true
  }
}
```

## Testing the API

To test the API, run the following command

```bash
python test_api.py
```

This script will send a request to the `/api/lbw-decision` endpoint using a sample input file located at `data/sample_input_lbw.json`.
