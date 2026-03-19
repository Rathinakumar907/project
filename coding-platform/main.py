import uvicorn
import webbrowser
import threading
import time
import sys
import os

def open_browser():
    """Opens the browser after a short delay to allow the server to start."""
    time.sleep(2)  # Wait for the server to initialize
    print("\n[INFO] Automatically opening application in browser: http://localhost:8000")
    webbrowser.open("http://localhost:8000")

def start_server():
    """Starts the FastAPI server using uvicorn."""
    print("[INFO] Starting University Coding Platform...")
    try:
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure we are in the project root (where this file is located)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Start the browser thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start the server (this is blocking)
    start_server()
