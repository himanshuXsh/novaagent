FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (psycopg2 needs libpq-dev and gcc)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (for layer caching)
COPY requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the entire backend directory into /app/backend
# This ensures imports like `from backend.gateway...` work correctly
COPY . /app/backend

# Run migrations then start the server
CMD ["python", "backend/run.py"]
