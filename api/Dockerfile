FROM python:3.11.0-alpine3.16 as base

WORKDIR /usr/src/app

ENV \
# Turns off writing .pyc files
	PYTHONDONTWRITEBYTECODE=1 \
# Seems to speed things up
	PYTHONUNBUFFERED=1 \
# Default VENV usage
	PATH="/venv/bin:${PATH}" \
	VIRTUAL_ENV="/venv"

### ---
FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Install dev dependencies
RUN apk update && \
	apk add --no-cache gcc libffi-dev musl-dev postgresql-dev make

COPY Makefile ./Makefile

# Create virtual env to store dependencies
RUN python3 -m venv /venv 

# Install deps
RUN pip3 install -U pip && \
	pip3 install setuptools && \
    pip install wheel && \
    pip wheel . --wheel-dir=/venv/wheels

RUN . /venv/scripts/activate && \
    pip install --no-index --find-links=/venv/wheels -r requirements.txt

### ---
FROM base as final

RUN apk add --no-cache libffi libpq

COPY --from=builder /venv /venv
COPY --from=builder /usr/src/app .

EXPOSE 8000