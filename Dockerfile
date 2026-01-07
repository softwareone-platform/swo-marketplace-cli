FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

WORKDIR /cli

COPY pyproject.toml uv.lock ./
RUN uv venv /opt/venv

ENV VIRTUAL_ENV=/opt/venv
ENV PATH=/opt/venv/bin:$PATH

FROM base AS build

COPY . /cli

RUN uv sync --frozen --no-cache --all-groups --active

FROM build AS dev

CMD ["bash"]
