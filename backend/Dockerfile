FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if any needed (e.g. for psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory into /app/backend
# so that imports like `backend.main` work correctly
COPY . /app/backend

# The command to run FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
