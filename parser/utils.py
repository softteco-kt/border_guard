from models import BorderCapture, database
from send_msg import send_to_qu
from PIL import Image

import requests
import io
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


def is_black(img: Image, threshold=0.99):

    # check if img is a url
    if img.startswith("http"):
        img_bytes = requests.get(img, stream=True).raw
        img = Image.open(io.BytesIO(img_bytes))

    try:
        # convert to grayscale
        pixels = img.convert("L").getdata()  # get the pixels as a flattened sequence
    except Exception as ex:
        print(ex)
        raise Exception("Custom exception: Image is not valid. Perhaps url is broken?")

    nblack, black_thresh = 0, 50

    # count black pixels in image
    for pixel in pixels:
        if pixel < black_thresh:
            nblack += 1

    black_pixels_proportion = nblack / float(len(pixels))
    if black_pixels_proportion > threshold:
        return True
    else:
        return False


def is_similar(image_url_1, image_url_2, url: bool = False):
    if url:
        image_url_1 = requests.get(image_url_1, stream=True).raw
        image_url_2 = requests.get(image_url_2, stream=True).raw
    return image_url_1 == image_url_2
