import uvicorn
import logging
from main import app

def start_server():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

if __name__ == "__main__":
    start_server()
