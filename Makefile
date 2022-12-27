install:
	poetry install

run:
	poetry run python main.py

run-d:
	nohup poetry run python -u main.py > output.logs &