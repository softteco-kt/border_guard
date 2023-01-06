install:
	poetry install

run:
	poetry run python main.py

server-setup:
	apt install python3-poetry

chrome:
	wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
	sudo apt-get install google-chrome-stable ./google-chrome-stable_current_amd64.deb

run-cron:
	(crontab -l ; cat cron.env ; echo "*/20 * * * * $(poetry run which python) $(pwd)/test.py >> $(pwd)/logs.log 2>&1")| crontab -