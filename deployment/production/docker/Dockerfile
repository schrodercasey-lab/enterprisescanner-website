
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.production.txt .
RUN pip install --no-cache-dir -r requirements.production.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash enterprise
RUN chown -R enterprise:enterprise /app
USER enterprise

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "stable_server:app"]
