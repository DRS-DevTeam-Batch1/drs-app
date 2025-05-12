from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from output import get_module_output
import os
import tempfile
import shutil
from typing import Optional
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import requests

app = FastAPI(title="Cricket Video Analysis API",
              description="API for analyzing cricket videos using computer vision",
              version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create a temporary directory for uploaded files
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "cricket_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create a directory for output files
OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "cricket_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Try to mount the static directories
try:
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
    app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
except Exception as e:
    print(f"Warning: Could not mount static directories: {e}")

@app.get("/")
async def root():
    """Root endpoint that returns HTML interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cricket Video Analysis</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                color: #2c3e50;
            }
            .container {
                border: 1px solid #ddd;
                padding: 20px;
                border-radius: 5px;
                margin-top: 20px;
            } 
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #2980b9;
            }
            #results {
                margin-top: 20px;
                padding: 10px;
                border: 1px solid #eee;
                display: none;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                animation: spin 2s linear infinite;
                display: none;
                margin-left: 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            img {
                max-width: 100%;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Cricket Video Analysis</h1>
        <div class="container">
            <div class="form-group">
                <label for="videoFile">Upload Cricket Video:</label>
                <input type="file" id="videoFile" accept=".mp4,.avi,.mov">
            </div>
            <div class="form-group">
                <button onclick="uploadVideo()">Analyze Video</button>
                <div class="spinner" id="spinner"></div>
            </div>
            <div id="results">
                <h2>Analysis Results</h2>
                <pre id="resultJson"></pre>
                <div id="visualization"></div>
            </div>
        </div>

        <script>
            async function uploadVideo() {
                const fileInput = document.getElementById('videoFile');
                const resultsDiv = document.getElementById('results');
                const resultJson = document.getElementById('resultJson');
                const spinner = document.getElementById('spinner');
                const visualizationDiv = document.getElementById('visualization');

                if (!fileInput.files[0]) {
                    alert('Please select a video file');
                    return;
                }

                const formData = new FormData();
                formData.append('video', fileInput.files[0]);

                resultsDiv.style.display = 'none';
                spinner.style.display = 'inline-block';

                try {
                    const response = await fetch('/api/analyze-video', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();

                    resultJson.textContent = JSON.stringify(data, null, 2);
                    resultsDiv.style.display = 'block';

                    // Display visualization if available
                    visualizationDiv.innerHTML = '';
                    if (data.status === 'success' && data.data.visualization) {
                        const img = document.createElement('img');
                        img.src = 'data:image/png;base64,' + data.data.visualization;
                        visualizationDiv.appendChild(img);
                    }
                } catch (error) {
                    resultJson.textContent = 'Error: ' + error.message;
                    resultsDiv.style.display = 'block';
                } finally {
                    spinner.style.display = 'none';
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# @app.post("/api/analyze-video")
# async def analyze_video(video: UploadFile = File(...)):
#     """Endpoint to upload and analyze a cricket video"""
#     if not video.filename:
#         raise HTTPException(status_code=400, detail="No video file uploaded")

#     # Check file extension
#     file_extension = os.path.splitext(video.filename)[1].lower()
#     if file_extension not in ['.mp4', '.avi', '.mov']:
#         raise HTTPException(status_code=400, detail="Unsupported file format. Please upload MP4, AVI, or MOV files.")

#     # Create a temporary file path
#     temp_file_path = os.path.join(UPLOAD_DIR, video.filename)

#     try:
#         # Save the uploaded file
#         with open(temp_file_path, "wb") as buffer:
#             shutil.copyfileobj(video.file, buffer)

#         # Process the video
#         result = get_module_output(temp_file_path)

#         return JSONResponse(content=result)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

#     finally:
#         # Clean up the file
#         if os.path.exists(temp_file_path):
#             try:
#                 os.remove(temp_file_path)
#             except:
#                 pass  # Ignore cleanup errors

@app.post("/api/analyze-video")
async def analyze_video(video: UploadFile = File(...)):
    """Endpoint to upload and analyze a cricket video"""
    if not video.filename:
        raise HTTPException(status_code=400, detail="No video file uploaded")
    print("recieved")
    # Check file extension
    file_extension = os.path.splitext(video.filename)[1].lower()
    if file_extension not in ['.mp4', '.avi', '.mov']:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload MP4, AVI, or MOV files.")

    # Create a temporary file path
    temp_file_path = os.path.join(UPLOAD_DIR, video.filename)

    try:
        # Save the uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        # Process the video (placeholder for actual implementation)
        result = get_module_output(temp_file_path)
#         result = get_module_output(temp_file_path)
        #return JSONResponse(content=result)
        # Forward to Bat's Edge Detection Module
        print("Result from Mod 2:", result)

        bat_edge_response = requests.post("http://127.0.0.1:5000/detect_batedge", json=result["data"])


        # # Forward to Stream Analysis and Overlay Module
        # overlay_payload = {
        #     "module": "Ball and Object Tracking Module",
        #     "data": result
        # }
        # try:
        #     overlay_response = requests.post("http://127.0.0.1:8001/api/log-intermediate-data", json=overlay_payload)
        #     if overlay_response.status_code != 200:
        #         print(f"Failed to send to Overlay Module: {overlay_response.status_code}")
        # except Exception as e:
        #     print(f"Error sending to Overlay Module: {str(e)}")

        return JSONResponse(content=bat_edge_response.json())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

    finally:
        # Clean up the file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass  # Ignore cleanup errors


@app.get("/api/module-output")
def module_output():
    """Legacy endpoint from the skeleton"""
    return JSONResponse(content={
        "status": "error",
        "message": "This endpoint requires a video file. Please use /api/analyze-video endpoint instead."
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "Cricket Video Analysis API"}

# This allows the application to be run directly with Python
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 