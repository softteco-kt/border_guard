from models import BorderCapture, database
from send_msg import send_to_qu
import os


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
