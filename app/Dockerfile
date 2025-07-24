# === STAGE 1: Builder ===
FROM python:3.10-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --prefix=/install -r requirements.txt

# === STAGE 2: Runtime ===
FROM python:3.10-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy only required files (code and entrypoint)
COPY . .


# Make sure entrypoint is executable
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8000

# Run app
ENTRYPOINT ["./entrypoint.sh"]
