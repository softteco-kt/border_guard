from selenium.webdriver.common.by import By
from seleniumbase import page_actions

import datetime
import time
import logging
import os

import undetected_chromedriver as uc

from send_msg import send_to_qu, logger

from models import BorderCapture, init_db, database
import sys

URL = os.environ.get('URL')

RETRY_ATTEMTPS = 5

def fetch_image(retries = RETRY_ATTEMTPS):

    try:
        # Checking database connection
        database.connect()
    except:
        raise Exception("Database connection can not be established.")

    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
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
        logger.info(f'Successfuly fetched an image - {img_name}!')

        with database:
            model = BorderCapture.create(
                image_path=img_name,
            )
        
        # ID is of type UUID, thus conversion req.
        send_to_qu(str(model.id))
        logger.info("Sent to queue!")

    except Exception as e:
        
        if retries == 0:
            logger.exception(e); sys.exit(1)

        driver.quit(); time.sleep(3)
        logger.error(f'Fetch failed. Attempting retry...')
        fetch_image(retries=retries - 1)

    driver.quit()


if __name__ == "__main__":
    fetch_image()