FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend directory into /app/frontend
# Note: Since the app is launched via python -m streamlit run frontend/app.py
# we need to be in the parent directory of frontend
COPY . /app/frontend

CMD ["python", "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8502", "--server.address", "0.0.0.0"]
