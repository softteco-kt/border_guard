from PIL import Image

import io
import requests


def is_black(img: Image, threshold=0.99):

    # check if img is a url
    if img.startswith("http"):
        img_bytes = requests.get(img, stream=True).raw
        img = Image.open(io.BytesIO(img_bytes))

    # otherwise img should be an Image object
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
