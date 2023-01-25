import logging
import os
import sys

import pika

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")
RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT")
IMAGE_EXCHANGE = os.environ.get("IMAGE_EXCHANGE")
IMAGE_ROUTING_KEY = os.environ.get("IMAGE_ROUTING_KEY")
Q = os.environ.get("IMAGE_QUEUE")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s", "%m-%d-%Y %H:%M:%S"
)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)

logger.addHandler(stdout_handler)


def send_to_qu(msg: str):
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    )
    channel = conn.channel()

    # Create exchange
    channel.exchange_declare(exchange=IMAGE_EXCHANGE, exchange_type="topic")
    # create queue
    channel.queue_declare(queue=Q, durable=True)
    # bind queue
    channel.queue_bind(queue=Q, exchange=IMAGE_EXCHANGE, routing_key=IMAGE_ROUTING_KEY)

    # send msg to queue
    channel.basic_publish(
        exchange=IMAGE_EXCHANGE,
        routing_key=IMAGE_ROUTING_KEY,
        body=msg,
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        ),
    )
    logger.info("[client] Message sent!")
    # close conn to ensure successful delivery
    conn.close()


if __name__ == "__main__":
    RABBITMQ_HOST = "localhost"
    msg = input("<msg> to send:")
    send_to_qu(msg if msg is not None else "<default message>")
