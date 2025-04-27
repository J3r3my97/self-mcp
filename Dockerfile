# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    TRANSFORMERS_CACHE=/app/models \
    HF_HOME=/app/models \
    TORCH_HOME=/app/models \
    PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create models directory
RUN mkdir -p /app/models && chmod 777 /app/models

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create scripts directory and copy download script
RUN mkdir -p /app/scripts
COPY scripts/download_models.py /app/scripts/

# Pre-download all models
RUN python /app/scripts/download_models.py && \
    # Verify models were downloaded
    ls -la /app/models && \
    # Make models directory writable
    chmod -R 777 /app/models

# Copy project files
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Create directory for service account
RUN mkdir -p /app/config

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
