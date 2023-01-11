FROM python:3.10-slim-buster as base

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
    PIP_NO_CACHE_DIR=1 \
	WORKDIR=/usr/src/app

WORKDIR $WORKDIR

# Create virtual env to store dependencies
RUN python3 -m venv $VIRTUAL_ENV 
# Project dependencies
RUN apt-get update && apt-get -y install vim cron

### ---
FROM base as builder

RUN apt-get update && \ 
	apt-get -y install wget unzip

# Download Chrome and Chromedriver
RUN	wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    wget https://chromedriver.storage.googleapis.com/108.0.5359.71/chromedriver_linux64.zip && \
	unzip *.zip -d .

### ---
FROM base as final

ENV CHROME_EXE=google-chrome-stable_current_amd64.deb

COPY --from=builder \
	$WORKDIR/$CHROME_EXE \
	$WORKDIR/chromedriver \
	.
COPY requirements.txt .

# Install google-chrome
RUN apt-get -y install google-chrome-stable ./$CHROME_EXE && \
    rm ./$CHROME_EXE

RUN pip3 install -U pip && \
	pip3 install setuptools && \
	pip3 install -r requirements.txt

COPY . .

RUN mkdir data && touch logs.log && \
	sh cron.sh > /etc/cron.d/crontab && \
	chmod 0644 /etc/cron.d/crontab && \
	/usr/bin/crontab /etc/cron.d/crontab

# Run cron as main process
CMD ["cron", "-f"]