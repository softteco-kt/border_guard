HOME =: /bin/bash

up:
	docker compose --env-file=.env.compose up -d --build
down:
	docker compose down

# Send msg to queue
msg:
	@cd parser; python -m send_msg
