install:
	poetry install

run:
	poetry run python main.py

run-d:
	nohup poetry run python -u main.py > output.logs &

server-setup:
	apt install python3-poetry
	wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
	sudo apt-get install google-chrome-stable ./google-chrome-stable_current_amd64.deb