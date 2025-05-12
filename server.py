import uvicorn
import os

def main():
    server_host = os.getenv("HOST", "0.0.0.0")
    server_port = int(os.getenv("PORT", 8000))
    server_log_level = os.getenv("LOG_LEVEL", "info")

    uvicorn.run(
        "server:app",
        host=server_host,
        port=server_port,
        log_level=server_log_level,
        reload=False
    )

if __name__ == "__main__":
    main()
