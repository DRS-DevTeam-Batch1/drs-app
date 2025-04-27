import uvicorn
import os
from src.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    log_level = os.environ.get("LOG_LEVEL", "info")
    
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=False
    )