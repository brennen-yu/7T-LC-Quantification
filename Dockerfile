# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
# git: for version control
# build-essential: for compiling python extensions if needed
# procps: provides 'ps' command, often needed by workflow tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directories for bind mounting (standard PACE locations)
# We create these so we can map the HPC storage to them at runtime
RUN mkdir -p /data /outputs /atlases

# Set the default command to show help
CMD ["python", "src/config.py"]
