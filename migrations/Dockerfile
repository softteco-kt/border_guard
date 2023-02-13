FROM python:3.11.0-alpine3.16 as base

WORKDIR /usr/src/db

ENV \
# Turns off writing .pyc files
	PYTHONDONTWRITEBYTECODE=1 \
# Seems to speed things up
	PYTHONUNBUFFERED=1 \
# Default VENV usage
	PATH="/venv/bin:${PATH}" \
	VIRTUAL_ENV="/venv" \
# PIP configs
	PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Project dependencies
RUN apk add --no-cache libffi libpq
# Create virtual env to store dependencies
RUN python3 -m venv /venv 

### ---
FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Install dev dependencies
RUN apk update && \
	apk add --no-cache gcc libffi-dev musl-dev postgresql-dev
    
COPY requirements.txt .
RUN pip3 install -r requirements.txt

### ---
FROM base as final

COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

COPY . .

CMD ["sh", "docker-entrypoint.sh"]