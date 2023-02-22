import os
import functools
import traceback
import time

import requests

from models import BorderCapture, database
from send_msg import send_to_qu, logger


def retry(f_py=None, retries=1):
    """Decorator to retry a function call on failure N times."""

    def _decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            re = retries
            while re:

                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    time.sleep(3)
                    re -= 1
                    logger.error(traceback.format_exc(limit=1))
                    logger.info(
                        f"Failed. Retry attempt no.{retries - re}. In process ..."
                    )
                    if re == 0:
                        raise e

        return wrapper

    return _decorator(f_py) if f_py else _decorator


def write_untracked_images_to_db():
    # download all images from folder
    all_images = os.listdir("./data")

    with database:
        tracked_images = [i.image_path.split("/")[-1] for i in BorderCapture.select()]

        for image in all_images:

            if image in tracked_images:
                continue

            # Add database instance
            BorderCapture.insert(
                # image is separated by comma, e.g. 123456789.png
                created_at=float(image.split(".")[0]),
                # give absolute path of an image
                image_path="/usr/src/parser/data/" + image,
            ).execute()


def process_unprocessed_images():

    with database:
        # retrieve all unprocessed instance ids
        unprocessed_images = [
            instance.id
            for instance in BorderCapture.select().where(
                BorderCapture.processed == False
            )
        ]

        for image_id in unprocessed_images:
            # Send to queue for further processing
            send_to_qu(str(image_id))


def process_unvalidated_images():

    with database:
        images = BorderCapture.select().where(BorderCapture.is_valid == None)

        for image in images:

            # Check if the image is valid
            response = requests.post(
                "http://api:8000/is_valid", data={"image_path": image.image_path}
            )

            if response.status_code == 200:
                is_valid = True
                print(response)
            else:
                is_valid = False
                print(response, response.content)
            upd = BorderCapture.update(is_valid=is_valid).where(
                BorderCapture.id == image.id
            )
            upd.execute()
