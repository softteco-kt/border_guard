deps:
	pip3 install -r requirements.txt	
	pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu

up:
	docker container rm api || echo ""
	docker build -t api -f Dockerfile .
	docker run -d -p 8000:8000 --name api --env-file=../.env.compose api

down:
	docker container stop api

in:
	docker exec -it api sh