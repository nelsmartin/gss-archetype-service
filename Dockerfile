FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY gss_archetype_service ./gss_archetype_service

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

# data/ is intentionally not baked in. Mount the GSS file at runtime:
#   docker run -p 8000:8000 -v $(pwd)/data:/app/data gss-archetype-service
CMD ["uvicorn", "gss_archetype_service.service:app", "--host", "0.0.0.0", "--port", "8000"]
