## Worker microservice

Celery based worker microservice with [custom](https://docs.celeryq.dev/en/stable/userguide/extending.html#custom-message-consumers) message consumer. Worker consumes messages from specified Queues and Exchange with the help of Kombu consumer. 

The consumer works as a proxy, i.e. routes messages directly from Message Queue to celery tasks. This approach decouples other microservices that are dependent on this worker, such that, there is no need to know the names of tasks directly, e.g. 
> `celery_task.send_task(<task_name>, args, kwargs)`. 

It is only required to know the `Queues` / `Routing keys` that correspond with required tasks to send messages to workers.

Project can be started with `make` command ->
```sh
# Start as a standalone service with
make up
# Teardown
make down
```