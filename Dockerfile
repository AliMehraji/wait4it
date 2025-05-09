# Pin the Python base image for all stages and
FROM python:3.12-slim AS base

# install all shared dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Tweak Python to run better in Docker
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on 
    # PIP_INDEX_URL

# Build stage: dev & build dependencies can be installed here
FROM base AS build

# Install the compiler toolchain(s), dev headers, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# The virtual environment is used to "package" the application
# and its dependencies in a self-contained way.
RUN python -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip --timeout 100  install --no-cache-dir -r requirements.txt

# Runtime stage: copy only the virtual environment.
FROM base AS runtime

WORKDIR /app

RUN addgroup --gid 1001 --system nonroot && \
    adduser --no-create-home --shell /bin/false \
    --disabled-password --uid 1001 --system --group nonroot

USER nonroot:nonroot

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=build --chown=nonroot:nonroot /app/.venv /app/.venv
COPY --chown=nonroot:nonroot checker  /app/checker
COPY --chown=nonroot:nonroot main.py .

CMD ["python", "/app/main.py"]
