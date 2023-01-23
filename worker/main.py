from celery import Celery, bootsteps
from kombu import Consumer, Exchange, Queue

import os, sys, logging, requests

from .models import BorderCapture, database as database_connection


RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT')

IMAGE_QUEUE = os.environ.get("IMAGE_QUEUE")
IMAGE_EXCHANGE = os.environ.get("IMAGE_EXCHANGE")
IMAGE_ROUTING_KEY = os.environ.get("IMAGE_ROUTING_KEY")

FORMAT = '%(asctime)s - %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])

# Declare Kombu Queue
QUEUE = Queue(
        IMAGE_QUEUE, 
        Exchange(IMAGE_EXCHANGE, type='topic', durable=False), 
        routing_key=IMAGE_ROUTING_KEY
    )

class CustomConsumer(bootsteps.ConsumerStep):
    """ A proxy, routes messages directly from Message Queue to celery tasks"""

    def get_consumers(self, channel):
        return [Consumer(channel,
                         queues=[QUEUE],
                         callbacks=[self.handle_message]
                         )]

    def handle_message(self, body, message):
        logging.info(f'[consumer] Received {body}')
        process_img.delay(body)
        message.ack()

app = Celery(
    'worker', 
    backend='rpc://', 
    broker=f'pyamqp://{RABBITMQ_HOST}:{RABBITMQ_PORT}',
)

# Add a proxy class to celery application
app.steps['consumer'].add(CustomConsumer)

# Route messages from specified source to specific task
app.conf.task_routes = {
        'worker.main.process_img': {
            'queue': IMAGE_QUEUE, 
            'exchange':IMAGE_EXCHANGE, 
            'routing_key':IMAGE_ROUTING_KEY
        },
    }

# Declare Queues for celery to listen to
app.conf.task_queues = (
    QUEUE,
)

@app.task(acks_late=True)
def process_img(image_id):
    # init connection and automatically close when task is completed
    with database_connection:

        logging.info("[task] Received. ID: %r" % image_id)
        model = BorderCapture.get(id=image_id)

        # Model image_path is a url to static file
        response = requests.post(
            "http://api:8000/cars_on_border", 
            data={'image_url':model.image_path},
            # timeout for (connection , read)
            timeout=(5,30))

        if response.status_code != 200:
            # Temporary exception
            raise Exception

        try:
            response_amount = response.json()['amount']
        except:
            logging.error("[task] API wrong response")
            # temprorary exception
            raise Exception
        
        upd = model.update(
            number_of_cars=response_amount,
            processed=True
        )
        upd.execute()
        logging.info("[task] DB updated. ID: %r" % model.id)
        