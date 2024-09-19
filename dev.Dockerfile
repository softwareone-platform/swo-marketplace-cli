FROM python:3.12.2-bookworm
ENV PYTHONUNBUFFERED=1 POETRY_VERSION=1.7.0

RUN pip3 install poetry==$POETRY_VERSION

WORKDIR /swo

ADD . /swo

RUN poetry update && poetry install

CMD ["mpt-cli"]
