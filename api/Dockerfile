FROM python:3.10-slim-buster as base

WORKDIR /usr/src/app

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

# Install deps
RUN	pip3 install setuptools && \
	pip3 install -r requirements.lock.txt \ 
	--extra-index-url https://download.pytorch.org/whl/cpu

COPY . .

RUN chmod +x entrypoint-local.sh

EXPOSE 8000