HOME =: /bin/bash

deps:
	python -m venv .venv && \
		source .venv/scripts/activate && \
		pip3 install setuptools && \
		pip3 install --no-cache-dir -r requirements.lock.txt && \
		--extra-index-url https://download.pytorch.org/whl/cpu

compose:
	docker compose \
		--env-file=../.env.compose \
		up -d --build

up:
	docker container rm api || echo ""
	docker build -t api -f Dockerfile .
	docker run --rm -d -v .:/usr/src/api -p 8000:8000 --name api --env-file=../.env.compose api

down:
	docker container stop api

in:
	docker exec -it api sh