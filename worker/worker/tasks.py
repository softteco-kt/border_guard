import logging
import requests

from models import BorderCapture
from models import database as database_connection

from worker.main import app


@app.task(acks_late=True)
def process_img(image_id):
    # init connection and automatically close when task is completed
    with database_connection:

        logging.info("[task] Received. ID: %r" % image_id)
        model = BorderCapture.get(id=image_id)

        # Model image_path is a url to static file
        response = requests.post(
            "http://api:8000/cars_on_border",
            data={"image_url": model.image_path},
            # timeout for (connection , read)
            timeout=(5, 30),
        )

        if response.status_code != 200:
            # Temporary exception
            raise Exception

        try:
            response_amount = response.json()["amount"]
        except:
            logging.error("[task] API wrong response")
            # temprorary exception
            raise Exception

        upd = model.update(number_of_cars=response_amount, processed=True)
        upd.execute()
        logging.info("[task] DB updated. ID: %r" % model.id)
