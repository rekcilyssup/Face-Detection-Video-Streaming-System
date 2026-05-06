# Build stage
FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim

# Install system libraries needed by MediaPipe's internal cv2 import and curl for healthcheck
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 curl && rm -rf /var/lib/apt/lists/*

# Security: non-root user
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
COPY ./app /app/app
COPY ./tests /app/tests

# Make sure scripts in .local are usable
ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
