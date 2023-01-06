FROM python:3.9.0-alpine3.16

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

# Install poetry
RUN pip3 install -U pip && \
	pip3 install setuptools && \
	pip3 install poetry

# Create virtual env to store dependencies
RUN python3 -m venv /venv 

# Install root project
COPY pyproject.toml poetry.lock ./
RUN . /venv/bin/activate && poetry install --no-root --only main

# Build wheels
COPY . .
RUN . /venv/bin/activate && poetry build && pip install dist/*.whl

### ---
FROM base as final

RUN apk add --no-cache libffi libpq make

COPY --from=builder /venv /venv
COPY --from=builder /usr/src/app .

CMD ['./entrypoint.sh']