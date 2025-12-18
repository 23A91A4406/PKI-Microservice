# =========================
# Stage 1: Builder
# =========================
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# =========================
# Stage 2: Runtime
# =========================
FROM python:3.11-slim

# Set timezone to UTC
ENV TZ=UTC

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Configure timezone
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo UTC > /etc/timezone

# Copy installed python packages from builder
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY scripts /app/scripts
COPY data/seed.txt /app/seed.txt
COPY student_private.pem /app/scripts/
COPY cron_jobs /etc/cron.d
COPY requirements.txt /app/requirements.txt

# Set permissions for cron
RUN chmod 0644 /etc/cron.d/my_cron

# Register cron job
RUN crontab /etc/cron.d/my_cron

# Create volume mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Expose API port
EXPOSE 8080

# Start cron + API server
CMD ["sh", "-c", "cron && exec python3 /app/scripts/api_server.py"]


