FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy the leapx wheel from parent directory (build context is parent dir)
COPY ./leapx-0.0.1-py3-none-any.whl /tmp/leapx-0.0.1-py3-none-any.whl

# Copy application code first
COPY doc_processor/ .

# Update pyproject.toml and uv.lock to use the copied wheel path
RUN sed -i 's|leapx @ file://.*leapx-0.0.1-py3-none-any.whl|leapx @ file:///tmp/leapx-0.0.1-py3-none-any.whl|g' pyproject.toml && \
    sed -i 's|path = "\.\./leapx-0.0.1-py3-none-any.whl"|path = "/tmp/leapx-0.0.1-py3-none-any.whl"|g' uv.lock && \
    sed -i 's|{ name = "leapx", path = "\.\./leapx-0.0.1-py3-none-any.whl" }|{ name = "leapx", path = "/tmp/leapx-0.0.1-py3-none-any.whl" }|g' uv.lock

# Install dependencies
RUN uv sync --frozen

# Expose health check port
EXPOSE 8001

# Run the worker
CMD ["uv", "run", "python", "main.py"]
