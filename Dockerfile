# Build the Shifa AI Clinical Documentation Assistant into a container image.
FROM python:3.13-slim

# Keep Python output unbuffered (logs appear immediately) and skip .pyc files.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first so Docker can cache this layer when only code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY backend ./backend

EXPOSE 8000

# Listen on 0.0.0.0 so the server is reachable from outside the container.
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
