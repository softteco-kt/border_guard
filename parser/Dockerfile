FROM python:3.10-slim-buster as base

ENV \
	WORKDIR=/usr/src/app \
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
	apt-get -y install vim cron

### ---
FROM base as builder

RUN apt-get update && \
	apt-get -y install wget unzip
# Download Chrome and Chromedriver
RUN wget \
		--no-verbose \
		-O $CHROME_EXE \
		https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb && \
    wget \
		-O $CHROMEDRIVER_ZIP \
		https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
	unzip $CHROMEDRIVER_ZIP -d .

### ---
FROM base as final

# Install google-chrome
COPY --from=builder $WORKDIR/$CHROME_EXE $WORKDIR/chromedriver .

RUN apt install -y ./$CHROME_EXE && \
	rm ./$CHROME_EXE

COPY requirements.txt .
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