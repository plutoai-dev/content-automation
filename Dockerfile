# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (ffmpeg is required for video processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-root user for security (optional but recommended for Cloud Run)
# RUN useradd -m appuser && chown -R appuser /app
# USER appuser

# Environment variables will be injected by Cloud Run / Secret Manager
# But we can set defaults or placeholders if needed.

# Command to run the application
CMD ["python", "execution/main.py"]
