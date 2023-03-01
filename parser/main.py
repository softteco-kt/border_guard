import csv
import datetime
import os
import traceback

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from seleniumbase import page_actions

from models import BorderCapture, Camera, database
from send_msg import logger, send_to_qu
from utils import retry

RETRY_ATTEMTPS = 5


@retry(retries=RETRY_ATTEMTPS)
def fetch_image(url, location):

    if not url:
        url = os.environ["URL"]
    if not location:
        location = os.environ["URL_LOCATION"]

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=chrome")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options, driver_executable_path="./chromedriver")

    try:
        try:
            # Check the database connection before fetching the image
            database.connect(reuse_if_open=True)
        except:
            logger.error(traceback.format_exc(limit=1))
            raise Exception("Database connection can not be established.")

        driver.get(url)

        page_actions.wait_for_element(driver, selector="videoImage", by=By.ID)

        image = driver.find_element(By.ID, "videoImage")
        image_name = str(int(datetime.datetime.utcnow().timestamp())) + ".png"

        image_location = location + "/" + image_name

        # Save image to folder with a relative location
        image.screenshot("./data/" + image_location)

        assert image_name in os.listdir("./data/" + location + "/")
        logger.info(
            f"[parser] Successfuly fetched an image - {image_name} at {location}!"
        )

        camera_id = Camera.get_or_create(location_name=location)[0].id

        model = BorderCapture.create(
            camera_id=camera_id,
            image_path=os.getcwd() + "/data/" + image_location,
        )
        database.close()
    except Exception as e:
        driver.quit()
        raise e
    driver.quit()
    # ID is of type UUID, thus conversion req.
    return str(model.id)


if __name__ == "__main__":

    with open("urls.csv", "r") as f:

        sources = csv.reader(f)

        for row in sources:

            url, location = row

            image_id = fetch_image(url, location)
            send_to_qu(image_id)
