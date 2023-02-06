from functools import lru_cache
from io import BytesIO
from enum import Enum

import requests
import torch
from fastapi import Body, Depends, FastAPI, File, HTTPException, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps

from db import database, BorderCapture, AxisAlignedBoundingBoxNorm

from schemas import BorderCaptureOut, CarsMetaData

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serves static files from a shared volume with parser microservice
app.mount("/static", StaticFiles(directory="/usr/src/parser/data"), name="static")


class Yolov5(str, Enum):
    """YOLOv5 available model distribution/size names."""

    nano = "yolov5n"
    small = "yolov5s"
    medium = "yolov5m"
    large = "yolov5l"
    extra = "yolov5x"


@lru_cache
def get_model(model_size: Yolov5 = Yolov5.nano):
    """
    Given the model distribution name, downloads model i.e. saved parameters
    and weights of pre-trained model, to current directory.
    """
    return torch.hub.load(
        "ultralytics/yolov5", model_size, pretrained=True, force_reload=False
    )


@app.on_event("startup")
def startup():
    # Create DB if not exists
    database.connect()
    database.create_tables([BorderCapture, AxisAlignedBoundingBoxNorm])
    database.close()

    # Download and cache Yolov5 model variants
    for i in Yolov5:
        get_model(i)


@app.get("/cars_on_border", response_model=list[BorderCaptureOut])
async def get_db_information(
    processed: bool | None = None,
    start_timestamp: int | None = None,
    end_timestamp: int | None = None,
    offset: int | None = None,
    limit: int | None = None,
):
    with database:
        query = BorderCapture.select()

        if start_timestamp:
            query = query.where(BorderCapture.created_at >= start_timestamp)
        if end_timestamp:
            query = query.where(BorderCapture.created_at <= end_timestamp)
        if processed:
            query = query.where(BorderCapture.processed == processed)

        # If neither of timestamps are given, set default or given offset / limit
        if not any([start_timestamp, end_timestamp]):
            # Set default values if not provided
            if not offset:
                offset = 0
            if not limit:
                limit = 50

            query = query.offset(offset).limit(limit)
        # Otherwise set offset and limit only if they are provided in params
        else:
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

        return list(query.order_by(BorderCapture.created_at.desc()))


@app.post("/cars_on_border", response_model=CarsMetaData)
async def count_cars_in_image(
    image_url: str = Body(None),
    image_path: str = Body(None),
    image_binary: UploadFile = File(None),
    apply_grayscale: bool = False,
    model=Depends(get_model),
):
    if not any([image_url, image_binary, image_path]):
        raise HTTPException(
            status_code=422,
            detail={
                "field error": "At least one of the values should be provided",
                "values": {
                    "image_url": image_url,
                    "image_path": image_path,
                    "image_binary": image_binary,
                },
            },
        )

    try:
        # Open image
        if image_binary:
            image_to_process = Image.open(BytesIO(await image_binary.read()))
        elif image_url:
            response = requests.get(image_url)
            image_to_process = Image.open(BytesIO(response.content))
        elif image_path:
            image_to_process = Image.open(image_path, "r")
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
