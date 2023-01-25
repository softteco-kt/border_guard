import os

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT')

IMAGE_QUEUE = os.environ.get("IMAGE_QUEUE")
IMAGE_EXCHANGE = os.environ.get("IMAGE_EXCHANGE")
IMAGE_ROUTING_KEY = os.environ.get("IMAGE_ROUTING_KEY")