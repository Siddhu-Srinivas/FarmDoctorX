FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port
EXPOSE 8000

# Run with uvicorn in development, or gunicorn in production
# Render/Railway will automatically provide the PORT env var
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
