import datetime
import logging
import sys

import requests

from models import BorderCapture
from models import database as database_connection
from worker.main import app

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s", "%m-%d-%Y %H:%M:%S"
)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)

logger.addHandler(stdout_handler)


@app.task(acks_late=True)
def process_img(image_id):
    # init connection and automatically close when task is completed
    with database_connection:

        # Check if retrieved image is valid
        image_is_valid = requests.post(
            "http://api:8000/is_valid", data={"image_id": image_id}
        )

        if image_is_valid:

            # Model image_path is a url to static file
            response = requests.post(
                "http://api:8000/cars_on_border",
                # Use the biggest YOLO model
                params={"model_size": "yolov5x"},
                data={"image_id": image_id},
                # timeout for (connection , read)
                timeout=(5, 30),
            )
            if response.status_code != 200:
                # Temporary exception
                raise Exception("Non 200 API Response")
            try:
                number_of_cars = response.json()["amount"]
            except:
                logger.error("[task] API wrong response")
                # temprorary exception
                raise Exception("Key error: [amount] was not found in Response")
        else:
            number_of_cars = None

        upd = BorderCapture.update(
            number_of_cars=number_of_cars,
            processed_at=datetime.datetime.utcnow().timestamp(),
            processed=True,
            is_valid=image_is_valid,
        ).where(BorderCapture.id == image_id)
        upd.execute()

        logger.info("[task] DB updated. ID: %r" % image_id)
