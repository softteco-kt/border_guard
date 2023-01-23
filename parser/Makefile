SHELL := /bin/bash

run:
	source .venv/bin/activate && python3 main.py

run-cron:
	(source cron.sh)| crontab -
	echo "cron job set up successfully!"
	crontab -l

server-setup:
	source setup.sh && \
	wget --no-verbose -O /tmp/chrome.deb \
		https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb && \
		sudo apt-get update && \
		sudo apt install -y --allow-downgrades /tmp/chrome.deb && \
		rm /tmp/chrome.deb		

docker: 
	docker build . -t parser 

docker-run:
	docker run --rm -it -d --name parser parser 
	docker exec -it parser sh

docker-stop: 
	docker container stop parser 