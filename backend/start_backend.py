import uvicorn
import os
import sys

if __name__ == "__main__":
    # Ensure working directory is the backend directory so main can resolve paths correctly
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    print("Starting Coffee Journal Backend Server...")
    print("API Base URL: http://127.0.0.1:8000/api")
    print("Frontend App: http://127.0.0.1:8000/")
    
    # Run uvicorn programmatically
    try:
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
    except KeyboardInterrupt:
        print("\nStopping Coffee Journal Backend Server...")
        sys.exit(0)
