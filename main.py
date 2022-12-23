from selenium.webdriver.common.by import By
from seleniumbase import Driver
from seleniumbase import page_actions

import datetime
import time
import logging 
import os

FORMAT = '%(asctime)s - %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

URL = os.environ.get('URL')

def fetch_image():
    driver = Driver(uc=True)
    
    try:
        driver.get(URL)
        page_actions.wait_for_element(driver, selector="videoImage", by=By.ID)
        
        image = driver.find_element(By.ID, "videoImage")
        img_name = str(int(datetime.datetime.utcnow().timestamp())) + ".png"
        image.screenshot("./data/" + img_name)
        
        assert img_name in os.listdir("./data/")
        logging.info(f'Successfuly fetched an image - {img_name}!')
    except Exception as e:
        logging.error('->', exc_info=True)

    driver.quit()

if __name__ == "__main__":
    logging.info("Application startup...")
    try:
        logging.info(f'Started fetching...')
        while True:
            fetch_image()
            time.sleep(1200) # 20 min sleep
    except KeyboardInterrupt:
        logging.info(f'Exiting application...')
