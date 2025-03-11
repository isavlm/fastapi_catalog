# Base image
FROM --platform=linux/amd64 python:3.10-slim-bullseye AS base_image

RUN apt-get update && \
  apt-get install -y \
  libpq-dev \
  gcc && \
  apt-get clean -y

WORKDIR /ioet_catalog

COPY ./api ./api
COPY ./app ./app
COPY ./adapters ./adapters
COPY ./factories ./factories
COPY ./pyproject.toml ./
COPY ./poetry.lock ./
COPY ./main.py ./

RUN pip install poetry && \
  poetry config virtualenvs.create false

# Development image
FROM base_image as dev

RUN poetry install --no-root

ENV PORT=8000
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]