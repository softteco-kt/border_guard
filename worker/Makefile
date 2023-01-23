up:
	docker container rm worker || echo ""
	docker build -t worker -f celery.Dockerfile .
	docker run -d --name worker --env-file=../.env.compose worker
	winpty docker exec -it worker sh
down:
	docker container stop worker