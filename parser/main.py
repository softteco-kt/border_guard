import datetime
import os
import traceback

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from seleniumbase import page_actions

from models import BorderCapture, Camera, database
from send_msg import logger, send_to_qu
from utils import retry

URL = os.environ["URL"]
CAMERA_LOCATION = os.environ["URL_LOCATION"]

RETRY_ATTEMTPS = 5


@retry(retries=RETRY_ATTEMTPS)
def fetch_image():
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

        driver.get(URL)

        page_actions.wait_for_element(driver, selector="videoImage", by=By.ID)

        image = driver.find_element(By.ID, "videoImage")
        image_name = str(int(datetime.datetime.utcnow().timestamp())) + ".png"

        image_location = CAMERA_LOCATION + "/" + image_name

        # Save image to folder with a relative location
        image.screenshot("./data/" + image_location)

        assert image_name in os.listdir("./data/" + CAMERA_LOCATION + "/")
        logger.info(
            f"[parser] Successfuly fetched an image - {image_name} at {CAMERA_LOCATION}!"
        )

        camera_id = Camera.get_or_create(location_name=CAMERA_LOCATION)[0].id

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
    image_id = fetch_image()
    send_to_qu(image_id)
