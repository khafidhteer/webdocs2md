# ===== Stage 1: Build =====
FROM python:3.12-slim AS builder

# Install system dependencies required by Playwright Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdk-pixbuf2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium browser
RUN playwright install chromium

# Copy source code
COPY src/ ./src/
COPY .env.example ./.env.example

# ===== Stage 2: Runtime =====
FROM python:3.12-slim AS runtime

# Install only runtime system dependencies for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdk-pixbuf2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy Playwright browsers from builder
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Copy source code
COPY --from=builder /app/src ./src/
COPY --from=builder /app/.env.example ./.env.example

# Create output directory
RUN mkdir -p /app/output

# Set default environment variables
ENV OUTPUT_DIR=/app/output
ENV PLAYWRIGHT_HEADLESS=true

# Default command — users provide the URL as argument
ENTRYPOINT ["python", "-m", "src.cli"]
CMD ["--help"]