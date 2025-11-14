# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p src/static/uploads && chmod 755 src/static/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=application.py

# Expose port (Cloud Run uses PORT env var, but we'll default to 8080)
EXPOSE 8080

# Use gunicorn to run the application
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 2 --timeout 120 --access-logfile - --error-logfile - application:application

