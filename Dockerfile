
FROM python:3.9-slim

# ── Metadata ──────────────────────────────────────────────────────────────
LABEL maintainer="security-test@example.com"
LABEL description="Intentionally vulnerable app for Trivy scanning"
LABEL version="1.0.0"


# ── ❌ Misconfig: hardcoded secrets in ENV ─────────────────────────────────
ENV SECRET_KEY="super_secret_hardcoded_key_12345" \
    DB_PASSWORD="admin123" \
    AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE" \
    AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" \
    FLASK_ENV="development" \
    FLASK_DEBUG="1"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        wget \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# ── Install vulnerable Python dependencies ────────────────────────────────
COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# ── Copy application source code────────────────────────────────────────────────
COPY app/ ./app/

# ── Create data directory for path-traversal demo ─────────────────────────
RUN mkdir -p /app/data && echo "sample content" > /app/data/readme.txt

# ── ❌ Misconfig: exposing sensitive port without restriction ───────────────
EXPOSE 5000

# ── ❌ Misconfig: no HEALTHCHECK defined ──────────────────────────────────
# (Trivy will flag missing HEALTHCHECK)

# ── ❌ Misconfig: running app directly as root in debug mode ───────────────
CMD ["python", "app/main.py"]
