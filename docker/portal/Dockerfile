FROM python:3.13-slim

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

RUN uv pip install packages/cds-core --system
RUN uv pip install packages/cds-portal --system

EXPOSE 8865

CMD ["solara", "run", "cds_portal.pages", "--host=0.0.0.0", "--port=8865", "--no-open", "--production"]
