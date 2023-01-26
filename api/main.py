from functools import lru_cache
from io import BytesIO

import torch
import cv2
import numpy as np

from fastapi import Body, Depends, FastAPI, File, HTTPException, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps
from pydantic import BaseModel

from image_processing.night_illumination import dehaze

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from enum import Enum


class Yolov5(str, Enum):
    nano = "yolov5n"
    small = "yolov5s"
    medium = "yolov5m"
    large = "yolov5l"
    extra = "yolov5x"


@lru_cache
def get_model(model_size: Yolov5 = Yolov5.nano):
    return torch.hub.load(
        "ultralytics/yolov5", model_size, pretrained=True, force_reload=False
    )


@app.on_event("startup")
def startup():
    # Download and cache Yolov5 model variants
    for i in Yolov5:
        get_model(i)


class CarsMetaData(BaseModel):
    amount: int


@app.post("/cars_on_border", response_model=CarsMetaData)
async def count_cars_in_image(
    image_url: str = Body(None),
    image_binary: UploadFile = File(None),
    apply_grayscale: bool = False,
    model=Depends(get_model),
):
    if not any([image_url, image_binary]):
        raise HTTPException(
            status_code=422,
            detail={
                "field error": "At least one of the values should be provided",
            },
        )

    try:
        # Open image
        if image_binary:
            image_to_process = Image.open(BytesIO(await image_binary.read()))
        elif image_url:
            image_to_process = Image.open(image_url, "r")
    except:
        raise HTTPException(status_code=404, detail={"ValueError": "Image Not Found."})

    if apply_grayscale:
        image_to_process = ImageOps.grayscale(image_to_process)

    result = model(image_to_process)
    return count_cars(result, model)


def count_cars(results, model):
    """Helper function for process_home_form()"""
    amount_ = 0

    for result in results.xyxy:
        for pred in result:
            class_name = model.model.names[int(pred[5])]
            if class_name == "car":
                amount_ += 1
    return CarsMetaData(amount=amount_).dict()


@app.get("/")
async def healthcheck():
    return {"Status": "OK"}
