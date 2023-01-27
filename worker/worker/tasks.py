import logging
import requests
import datetime
import sys

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

        model = BorderCapture.get(id=image_id)

        # Model image_path is a url to static file
        response = requests.post(
            "http://api:8000/cars_on_border",
            # Use the biggest YOLO model
            params={"model_size": "yolov5x"},
            data={"image_path": model.image_path},
            # timeout for (connection , read)
            timeout=(5, 30),
        )

        if response.status_code != 200:
            # Temporary exception
            raise Exception("Non 200 API Response")

        try:
            response_amount = response.json()["amount"]
        except:
            logger.error("[task] API wrong response")
            # temprorary exception
            raise Exception("Key error: [amount] was not found in Response")

        upd = BorderCapture.update(
            number_of_cars=response_amount,
            processed_at=datetime.datetime.utcnow().timestamp(),
            processed=True,
        ).where(BorderCapture.id == image_id)

        upd.execute()
        logging.info("[task] DB updated. ID: %r" % model.id)
