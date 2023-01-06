from fastapi import FastAPI, File, UploadFile, Depends
import torch

from PIL import Image
from io import BytesIO
from functools import lru_cache

app = FastAPI()

@lru_cache
def get_model():
    return torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True, force_reload = False)

@app.on_event("startup")
def startup():
    get_model()


from pydantic import BaseModel
class CarsMetaData(BaseModel):
    amount: int

@app.post("/process", response_model=CarsMetaData)
async def count_cars_in_image(image: UploadFile = File(), model = Depends(get_model)):
    # decode + process image with PIL
    result = model(Image.open(BytesIO(await image.read())))
    return count_cars(result,model)

def count_cars(results, model):
    ''' Helper function for process_home_form()'''
    amount_ = 0

    for result in results.xyxy:
        for pred in result:
            class_name = model.model.names[int(pred[5])]
            if class_name == "car": amount_ += 1
    return CarsMetaData(amount=amount_).dict()

@app.get("/")
async def healthcheck():
    return {"Status":"OK"}
