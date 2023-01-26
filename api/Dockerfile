FROM python:3.10-slim-buster as base

WORKDIR /usr/src/api

ENV \
	# Turns off writing .pyc files
	PYTHONDONTWRITEBYTECODE=1 \
	# Seems to speed things up
	PYTHONUNBUFFERED=1 \
	# Default VENV usage
	PATH="/venv/bin:${PATH}" \
	VIRTUAL_ENV="/venv" \
	PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

COPY ./requirements.lock.txt ./ 

# Create virtual env to store dependencies
RUN python3 -m venv $VIRTUAL_ENV

# Project dependencies
RUN apt-get update && \
	apt-get -y install libpq5

### ---
FROM base as builder

# Dependencies for psycopg2
RUN apt-get update && \
	apt-get -y install libpq-dev gcc

COPY requirements.txt .
RUN pip3 install -U pip && \
	pip3 install setuptools && \
	pip3 install -r requirements.txt \
	--extra-index-url https://download.pytorch.org/whl/cpu

FROM builder as final

COPY . .

RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

CMD ["sh", "./docker-entrypoint.sh"]