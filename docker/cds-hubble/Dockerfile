FROM public.ecr.aws/docker/library/python:3.13-slim

WORKDIR /app

RUN pip install uv \
    && apt-get update \
    && apt-get install -y build-essential \
    && apt-get -y install git clang curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY packages ./packages

ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync --package cds-core --package cds-hubble --locked --no-dev

EXPOSE 8765

CMD ["uvicorn", "cds_hubble.server:app", "--host=0.0.0.0", "--port=8765", "--workers=2"]
