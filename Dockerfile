# [FACT] Constitutional Guardian - Production Container for Google Cloud Run
# [HYPOTHESIS] Containerized deployment enables scalable federation nodes
# [ASSUMPTION] Cloud Run provides sufficient cold-start performance for live audio
# Cache-bust: 2026-03-05T21:05:00Z - Build: 38 - Gemini 1.5 flash stable

FROM python:3.11-slim

# [FACT] Set working directory
WORKDIR /app

# [FACT] Install system dependencies for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# [FACT] Copy application code and dependency files
COPY helix_code/ ./helix_code/
COPY tools/ ./tools/
COPY pyproject.toml ./

# [FACT] Upgrade packaging toolchain to pick up fixed pip/wheel/setuptools vendors.
RUN python -m pip install --no-cache-dir --upgrade     pip==25.3     wheel>=0.46.2     setuptools>=82.0.0

# [FACT] Install dependencies from synced requirements.txt
RUN python -m pip install --no-cache-dir -r helix_code/requirements.txt

# [FACT] Create non-root user for security (Cloud Run best practice)
RUN useradd -m -u 1000 helix && chown -R helix:helix /app
USER helix

# [FACT] Cloud Run requires PORT env var (default 8180)
ENV PORT=8180
ENV PYTHONPATH=/app/helix_code
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# [FACT] Expose port for Cloud Run
EXPOSE 8180

# [FACT] Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8180/health')" || exit 1

# [FACT] Start Constitutional Guardian service
# [HYPOTHESIS] Running directly via python solves module resolution issues in containers
CMD ["python", "helix_code/live_guardian.py"]
