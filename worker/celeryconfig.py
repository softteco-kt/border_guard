import os

from kombu import Consumer, Exchange, Queue

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT')

IMAGE_QUEUE = os.environ.get("IMAGE_QUEUE")
IMAGE_EXCHANGE = os.environ.get("IMAGE_EXCHANGE")
IMAGE_ROUTING_KEY = os.environ.get("IMAGE_ROUTING_KEY")

# Declare Kombu Queue
QUEUE = Queue(
        IMAGE_QUEUE, 
        Exchange(IMAGE_EXCHANGE, type='topic', durable=False), 
        routing_key=IMAGE_ROUTING_KEY
    )

BROKER_URL=f'pyamqp://{RABBITMQ_HOST}:{RABBITMQ_PORT}',

# List of modules to import when the Celery worker starts.
IMPORTS = ('worker.main',)

# Route messages from specified source to specific task
TASK_ROUTES = {
        'worker.main.process_img': {
            'queue': IMAGE_QUEUE, 
            'exchange':IMAGE_EXCHANGE, 
            'routing_key':IMAGE_ROUTING_KEY
        },
    }

# Declare Queues for celery to listen to
CELERY_QUEUES = (
    QUEUE,
)
