import os
import subprocess
import sys

def main():
    try:
        print("Running migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        
        port = os.environ.get("PORT", "10000")
        print(f"Starting Uvicorn on port {port}...")
        # Replace the current process with uvicorn so it handles signals properly
        os.execvp("uvicorn", ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", port])
    except Exception as e:
        print(f"Failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
