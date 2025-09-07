# syntax=docker/dockerfile:1

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose the default port (can be overridden)
EXPOSE 8000

# Entrypoint for SSE (default)
CMD ["python", "server.py"]
