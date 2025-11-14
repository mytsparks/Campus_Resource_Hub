# Use Python 3.10 slim image (matches README requirement)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies including build tools for numpy/scikit-learn
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory with proper permissions
RUN mkdir -p src/static/uploads && chmod 755 src/static/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=application.py
ENV PORT=8080

# Expose port (Cloud Run sets PORT automatically)
EXPOSE 8080

# Use gunicorn to run the application
# Cloud Run will set PORT env var automatically
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 --access-logfile - --error-logfile - application:application

