# Root Dockerfile so platform scanners (Cloud 66, Heroku container registry, etc.) can detect the app.
# It reuses the application code under the `bot/` subdirectory.

FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install dependencies from the subfolder
COPY bot/requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY bot/ .

# Ensure runtime directories exist and mark as volumes (for Cloud 66 persistent mounts)
RUN mkdir -p sessions downloads
VOLUME ["/app/sessions", "/app/downloads"]

CMD ["python", "main.py"]
