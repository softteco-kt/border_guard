from PIL import Image
import requests
import io
import datetime
from models import BorderCapture, database

if __name__ == "__main__":

    database.connect()

    images = BorderCapture.select().where(BorderCapture.is_valid == None).all()

    for image in images:

        image_url = "http://api:8000/static/" + image.image_path.split("/")[-1]

        # Check if the image is valid
        response = requests.post(
            "http://api:8000/is_valid", data={"image_url": image_url}
        )

        if response.status_code == 200:
            # BorderCapture.update(
            #     is_valid=True,
            # ).where(BorderCapture.id == image.id)
            print(image_url, "is valid")

    database.close()
