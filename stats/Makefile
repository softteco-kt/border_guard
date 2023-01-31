docker: 
	docker build . -t stats 

docker-run:
	docker run --rm -it -d -v $(pwd):/usr/src/stats -p 8501:8501 --name stats --env-file=../.env.compose stats 

docker-in:
	docker exec -it stats bash

docker-stop: 
	docker container stop stats

re:
	docker container stop stats
	docker build . -t stats 
	docker run --rm -it -d -v $(pwd):/usr/src/stats -p 8501:8501 --name stats --env-file=../.env.compose stats
