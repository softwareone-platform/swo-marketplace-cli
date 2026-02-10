FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

WORKDIR /cli

RUN uv venv /opt/venv

ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH=/opt/venv/bin:$PATH

FROM base AS build

COPY . .

RUN uv sync --frozen --no-cache --no-dev

FROM build AS dev

RUN uv sync --frozen --no-cache --dev

CMD ["bash"]

FROM build AS prod

RUN rm -rf tests/

RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser && \
    mkdir -p /home/appuser/.cache/uv && \
    chown -R appuser:appuser /cli /opt/venv /home/appuser

ENV UV_CACHE_DIR=/home/appuser/.cache/uv

USER appuser

CMD ["bash"]
