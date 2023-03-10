import datetime
import logging
import sys
import traceback

import requests
import celery

from models import BorderCapture
from models import database as database_connection
from worker.main import app

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s", "%m-%d-%Y %H:%M:%S"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.setFormatter(formatter)

# stdout_handler = logging.StreamHandler(sys.stdout)
# stdout_handler.setLevel(logging.INFO)
# stdout_handler.setFormatter(formatter)

# logger.addHandler(stdout_handler)


class LogErrorsTask(celery.Task):
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 5}
    retry_backoff = 30

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logger.info(
            f"Task {task_id} with args: {args} failed. Retries left, {self.max_retries - self.request.retries + 1}. Exception: {exc}"
        )
        # logger.exception(f"Task failed with exception: {exc}")
        return super().on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.info(f"{task_id} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)


@app.task(base=LogErrorsTask, bind=True, ack_late=True, ignore_result=True)
def process_img(self, image_id):
    # init connection and automatically close when task is completed
    with database_connection:

        # Check if retrieved image is valid
        is_valid_response = requests.post(
            "http://api:8000/is_valid",
            data={"image_id": image_id},
            timeout=(5, 30),
        )

        try:
            # Check API accessibility (whether it works or not)
            assert is_valid_response.status_code == 200, is_valid_response.json()
        except Exception as e:
            logger.error(f"{is_valid_response.json()}, {traceback.format_exc(limit=1)}")
            raise Exception("API probably not accessible")

        is_valid = is_valid_response.json().get("is_valid")
        if is_valid:

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
            logger.info(f"[task] Image is not valid, {is_valid_response.json()}")
            number_of_cars = None

        upd = BorderCapture.update(
            number_of_cars=number_of_cars,
            processed_at=datetime.datetime.utcnow().timestamp(),
            processed=True,
            is_valid=is_valid,
        ).where(BorderCapture.id == image_id)
        upd.execute()

        logger.info("[task] DB updated. ID: %r" % image_id)
