FROM python:3.10-slim-buster as base

ENV \
	WORKDIR=/usr/src/parser \
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
    PIP_NO_CACHE_DIR=1 \
	# Chrome versions
	CHROMEDRIVER_VERSION=108.0.5359.71 \
	CHROME_VERSION=108.0.5359.71-1 \
	CHROME_EXE=chrome.deb \
	CHROMEDRIVER_ZIP=driver.zip

WORKDIR $WORKDIR
# Create virtual env to store dependencies
RUN python3 -m venv $VIRTUAL_ENV 
# Project dependencies
RUN apt-get update && \
	apt-get -y install vim cron libpq5 netcat

### ---
FROM base as builder

RUN apt-get update && \
	apt-get -y install wget unzip libpq-dev gcc
# Download Chrome and Chromedriver
RUN wget \
		--no-verbose \
		-O $CHROME_EXE \
		https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb && \
    wget \
		-O $CHROMEDRIVER_ZIP \
		https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
	unzip $CHROMEDRIVER_ZIP -d .

COPY requirements.txt .
RUN pip3 install -U pip && \
	pip3 install setuptools && \
	pip3 install -r requirements.txt

### ---
FROM base as final

# Install google-chrome
COPY --from=builder $WORKDIR/$CHROME_EXE $WORKDIR/chromedriver ./
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

RUN apt install -y ./$CHROME_EXE && \
	rm ./$CHROME_EXE

COPY . .

RUN chmod +x ./wait-for &&\
	mkdir data && touch logs.log

CMD ["sh", "./docker-entrypoint.sh"]