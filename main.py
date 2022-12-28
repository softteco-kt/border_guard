from selenium.webdriver.common.by import By
from seleniumbase import page_actions

import datetime
import time
import logging
import os

import undetected_chromedriver as uc

FORMAT = '%(asctime)s - %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

URL = os.environ.get('URL')

def fetch_image():

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
        logging.info(f'Successfuly fetched an image - {img_name}!')
    except Exception as e:
        logging.error('->', exc_info=True); driver.quit(); time.sleep(3)
        logging.info(f'Fetch failed. Attempting retry...')
        fetch_image()

    driver.quit()


if __name__ == "__main__":
    fetch_image()