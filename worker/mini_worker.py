from kombu import Connection
from kombu.mixins import ConsumerMixin

from worker.env import *
from worker.consumer import QUEUE
from worker.tasks import process_img

from celeryconfig import broker_url

class Worker(ConsumerMixin):
    def __init__(self, connection, queues):
        self.connection = connection
        self.queues = queues

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self.queues, callbacks=[self.on_message])]

    def on_message(self, body, message):
        print("Got message: {0}".format(body))
        # process_img(body)
        message.ack()


if __name__ == "__main__":
    with Connection(broker_url, heartbeat=4) as conn:
        worker = Worker(conn, QUEUE)
        worker.run()
