FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY Pipfile ./
COPY Pipfile.lock ./

RUN apk add --no-cache \
    git \
    make \
    bash \
    build-base \
    libffi-dev \
    libressl-dev \
    postgresql-dev \
    postgresql-client \
    jpeg-dev \
    zlib-dev && \
  pip install coverage pipenv && \
  pipenv install --deploy --system

COPY . .

CMD ["scripts/docker-start"]