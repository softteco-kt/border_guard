import datetime
import os

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from seleniumbase import page_actions

from models import BorderCapture, Camera, database
from send_msg import logger, send_to_qu
from utils import retry

URL = os.environ["URL"]
URL_LOCATION = os.environ["URL_LOCATION"]

RETRY_ATTEMTPS = 3


@retry(retries=RETRY_ATTEMTPS)
def fetch_image():
    try:
        # Checking database connection
        database.connect()
    except:
        raise Exception("Database connection can not be established.")

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=chrome")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options, driver_executable_path="./chromedriver")

    try:
        driver.get(URL)

        page_actions.wait_for_element(driver, selector="videoImage", by=By.ID)

        image = driver.find_element(By.ID, "videoImage")
        img_name = str(int(datetime.datetime.utcnow().timestamp())) + ".png"
        image.screenshot("./data/" + img_name)

        assert img_name in os.listdir("./data/")
        logger.info(f"[parser] Successfuly fetched an image - {img_name}!")

        with database:
            camera_id = Camera.get_or_create(location_name=URL_LOCATION)[0].id

            model = BorderCapture.create(
                camera_id=camera_id,
                image_path=os.getcwd() + "/data/" + img_name,
            )
    except Exception as e:
        driver.quit()
        raise e
    driver.quit()

    # ID is of type UUID, thus conversion req.
    return str(model.id)


if __name__ == "__main__":
    image_id = fetch_image()
    send_to_qu(image_id)
