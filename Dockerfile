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
  pip install pipenv && \
  pipenv install --deploy --system

COPY . .

CMD ["gunicorn", "-w", "4", "posts.wsgi:application", "--bind", "0.0.0.0:8000"]