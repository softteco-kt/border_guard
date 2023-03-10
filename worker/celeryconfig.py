import logging
import sys

from worker.consumer import QUEUE
from worker.env import *

FORMAT = "%(asctime)s - %(levelname)s: %(message)s"
logging.basicConfig(
    format=FORMAT, level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)]
)

broker_url = (f"pyamqp://{RABBITMQ_HOST}:{RABBITMQ_PORT}/",)

# Number of CPU cores
worker_concurrency = 1

# The log level output to stdout and stderr
worker_redirect_stdouts_level = "INFO"

# Send task-related events that can be captured by monitors like celery events
worker_send_task_events = True

# List of modules to import when the Celery worker starts.
imports = ("worker.tasks",)
