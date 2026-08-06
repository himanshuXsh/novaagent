import os
import subprocess
import sys

def main():
    try:
        print("Running migrations...")
        alembic_args = ["alembic", "upgrade", "head"]
        if not os.path.exists("alembic.ini") and os.path.exists("backend/alembic.ini"):
            alembic_args = ["alembic", "-c", "backend/alembic.ini", "upgrade", "head"]
            
        subprocess.run(alembic_args, check=True)
        
        port = os.environ.get("PORT", "10000")
        print(f"Starting Uvicorn on port {port}...")
        
        uvicorn_app = "main:app"
        if not os.path.exists("main.py") and os.path.exists("backend/main.py"):
            uvicorn_app = "backend.main:app"
            
        # Replace the current process with uvicorn so it handles signals properly
        os.execvp("uvicorn", ["uvicorn", uvicorn_app, "--host", "0.0.0.0", "--port", port])
    except Exception as e:
        print(f"Failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
