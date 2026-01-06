# Stage 1: Build Go Engine
FROM golang:1.21-alpine AS builder

WORKDIR /app/engine
# Copy only necessary files for dependency download
COPY engine/go.mod engine/go.sum ./
RUN go mod download

# Copy the rest of the engine code
COPY engine/ .
# Build static binary
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/bin/engine main.go

# Stage 2: Python Runtime & Final Image
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python Code
COPY . .

# Copy Compiled Go Engine from Stage 1
COPY --from=builder /app/bin/engine /app/bin/engine

# Expose ports (API: 8000, gRPC: 50051)
EXPOSE 8000 50051

# Default command: Run API server (The user can also run CLI or Engine separately)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
