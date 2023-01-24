HOME =: /bin/bash

ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
# turn them into do-nothing targets
$(eval $(ARGS):;@:)

up:
	docker compose --env-file=.env.compose up -d --build
down:
	docker compose down

logs:
	docker compose logs $(ARGS) 
in:
	docker exec -it $(ARGS) bash
# Send msg to queue
msg:
	@cd parser; python -m send_msg
