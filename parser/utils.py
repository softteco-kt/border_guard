import os
from io import BytesIO

import imagehash
import requests

from models import BorderCapture, database
from PIL import Image
from send_msg import send_to_qu


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


def process_similar_imghash():
    with database:
        images = BorderCapture.select().where(BorderCapture.is_valid == True)

        for indx, image in enumerate(images):
            is_valid = True
            base_url = "http://api:8000/static/"
            assert image == images[indx]

            image1 = Image.open(
                BytesIO(
                    requests.get(
                        base_url + images[indx].image_path.split("/")[-1]
                    ).content
                )
            )
            image2 = Image.open(
                BytesIO(
                    requests.get(
                        base_url + images[indx - 1].image_path.split("/")[-1]
                    ).content
                )
            )

            ihash1 = imagehash.phash(image1)
            ihash2 = imagehash.phash(image2)

            if ihash1 == ihash2:
                is_valid = False
                print(
                    "image hashes are similar",
                    image.image_path,
                    images[indx - 1].image_path,
                )
                print("image hashes distance is equal to", ihash1 - ihash2)

            # upd = BorderCapture.update(is_valid=is_valid).where(
            #     BorderCapture.id == image.id
            # )
            # upd.execute()
