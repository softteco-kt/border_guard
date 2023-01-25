import logging

from celery import bootsteps
from kombu import Consumer, Exchange, Queue

from worker.env import *
from worker.main import app
from worker.tasks import process_img

# Declare Kombu Queue
QUEUE = Queue(
    IMAGE_QUEUE,
    Exchange(IMAGE_EXCHANGE, type="topic", durable=False),
    routing_key=IMAGE_ROUTING_KEY,
)


class CustomConsumer(bootsteps.ConsumerStep):
    """A proxy, routes messages directly from Message Queue to celery tasks"""

    def get_consumers(self, channel):
        return [Consumer(channel, queues=[QUEUE], callbacks=[self.handle_message])]

    def handle_message(self, body, message):
        logging.info(f"[consumer] Received {body}")
        process_img.delay(body)
        message.ack()


# Add a proxy class to celery application
app.steps["consumer"].add(CustomConsumer)
