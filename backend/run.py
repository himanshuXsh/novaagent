import os
import subprocess
import sys

def main():
    # Get the directory where this script lives (/app/backend inside Docker)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # The parent is /app — needed as PYTHONPATH so 'from backend.xxx' imports work
    app_dir = os.path.dirname(script_dir)

    # Change into backend dir so alembic finds alembic.ini and the alembic/ folder
    os.chdir(script_dir)
    print(f"Working directory: {script_dir}")

    # Ensure /app is on PYTHONPATH so 'from backend.xxx import' works for uvicorn
    pythonpath = os.environ.get("PYTHONPATH", "")
    if app_dir not in pythonpath:
        os.environ["PYTHONPATH"] = f"{app_dir}:{pythonpath}" if pythonpath else app_dir

    try:
        print("Running migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Migrations complete.")

        port = os.environ.get("PORT", "10000")
        print(f"Starting Uvicorn on port {port}...")

        # Use backend.main:app because main.py imports 'from backend.xxx'
        # PYTHONPATH=/app is already set above so Python can resolve it
        os.execvp("uvicorn", [
            "uvicorn", "backend.main:app",
            "--host", "0.0.0.0",
            "--port", port
        ])
    except Exception as e:
        print(f"Failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
