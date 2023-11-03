FROM python:3.10.5-slim-buster

WORKDIR /app

# set environment variables (prevent pyc files and stout and stderr)
ENV PYTHONDONTWRITEBYTECODE=1\
    PYTHONUNBUFFERED=1\
    POETRY_VERSION=1.5.1\
    PYTHONPATH=${PYTHONPATH}:${PWD} 

#COPY PROJECT
COPY ../. .
COPY ../pyproject.toml .


RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
