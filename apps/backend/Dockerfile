FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \ 
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock leapx-0.0.1-py3-none-any.whl ./

RUN pip install --no-cache-dir uv

RUN uv sync --frozen

# Add the virtual environment to PATH so commands are available
ENV PATH="/app/.venv/bin:$PATH"

COPY . .

RUN mkdir -p /tmp/uploads

EXPOSE 8000
#  this is only valid for single ecs task
CMD ["sh", "-c", "alembic upgrade head && python -m app.db.seeders.run_seeders && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000"]
