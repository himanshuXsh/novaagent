#!/bin/bash
echo "Running migrations..."
alembic upgrade head
echo "Starting Uvicorn..."
uvicorn main:app --host 0.0.0.0 --port $PORT
