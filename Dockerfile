FROM python:3.12-slim-trixie

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ADD . /app

RUN uv sync --locked

EXPOSE 8000

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
