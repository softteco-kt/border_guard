import datetime
import logging
import traceback
from enum import Enum
from functools import lru_cache
from io import BytesIO

import requests
import torch
from PIL import Image, ImageOps
from fastapi import Body, Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from weights import Yolov5
from db import AxisAlignedBoundingBoxNorm, Camera, BorderCapture, database
from schemas import BorderCaptureOut, CarsMetaData, CameraOut
from image_processing.utils import is_black, is_similar

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


@lru_cache
def get_model(model_size: Yolov5 = Yolov5.nano):
    """
    Given the model distribution name, downloads model i.e. saved parameters
    and weights of pre-trained model, to current directory.
    """
    return torch.hub.load(
        repo_or_dir="ultralytics/yolov5",
        source="github",
        model=model_size,
        force_reload=False,
        pretrained=True,
        verbose=False,
    )


@app.get("/camera_locations", response_model=list)
async def get_camera_locations():
    with database:
        return [camera.location_name for camera in Camera.select()]


@app.get("/cars_on_border", response_model=list[BorderCaptureOut])
async def get_db_information(
    location: str | None = None,
    processed: bool | None = None,
    start_timestamp: int | None = None,
    end_timestamp: int | None = None,
    offset: int | None = None,
    limit: int | None = None,
):
    with database:
        query = BorderCapture.select(
            BorderCapture.id,
            BorderCapture.created_at,
            BorderCapture.processed_at,
            BorderCapture.number_of_cars,
            BorderCapture.image_path,
            BorderCapture.is_valid,
            Camera.location_name,
        ).join(Camera)

        if start_timestamp:
            query = query.where(BorderCapture.created_at >= start_timestamp)
        if end_timestamp:
            query = query.where(BorderCapture.created_at <= end_timestamp)
        if processed:
            query = query.where(BorderCapture.processed == processed)
        if location:
            location_exists = Camera.get_or_none(Camera.location_name == location)
            if not location_exists:
                raise HTTPException(status_code=404, detail="Location does not exist.")
            query = query.where(Camera.location_name == location)

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


@app.post("/is_valid")
async def validate_photo_for_processing(
    image_id: str = Body(None),
    image_url: str = Body(None),
    image_binary: UploadFile = File(None),
):
    if not any([image_url, image_binary, image_id]):
        raise HTTPException(
            status_code=422,
            detail={
                "field error": "At least one of the values should be provided",
                "values": {
                    "image_id": image_id,
                    "image_url": image_url,
                    "image_binary": image_binary,
                },
            },
        )

    # Open image
    try:
        if image_binary:
            image_to_process = Image.open(BytesIO(await image_binary.read()))
        elif image_url:
            response = requests.get(image_url)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail={"Invalid URL": response.content},
                )
            image_to_process = Image.open(BytesIO(response.content))
        elif image_id:
            with database:
                image_path = BorderCapture.get(id=image_id).image_path
            image_to_process = Image.open(image_path, "r")
    except:
        raise HTTPException(status_code=404, detail={"ValueError": "Image Not Found."})

    # Retrieve last valid image from filesystem
    try:
        # Retrieve last valid image from database
        with database:
            # Retrieve timestamp from image
            input_image_instance = BorderCapture.get(id=image_id)
            input_image_timestamp = input_image_instance.created_at
            input_image_loc = input_image_instance.camera

            last_valid_image_instance = (
                BorderCapture.select(BorderCapture.image_path)
                .order_by(BorderCapture.processed_at.desc())
                .where(
                    BorderCapture.is_valid == True,
                    BorderCapture.camera_id == input_image_loc,
                    BorderCapture.created_at < input_image_timestamp
                    if image_id
                    else datetime.datetime.utcnow().timestamp(),
                )
                .limit(1)
                .first()
            )
        if not last_valid_image_instance:
            print("No valid preceding image found.")
        else:
            last_valid_image = Image.open(last_valid_image_instance.image_path, "r")

            if is_similar(image_to_process, last_valid_image):
                return {
                    "is_valid": False,
                    "detail": "Image is similar to previously processed one.",
                }
    except Exception as e:
        logging.exception(traceback.format_exc(limit=1))
        raise HTTPException(
            status_code=404,
            detail={
                "field error": "No image found in filesystem",
            },
        )

    if is_black(image_to_process):
        return {"is_valid": False, "detail": "Image is black"}
    return {"is_valid": True}


@app.post("/cars_on_border", response_model=CarsMetaData)
async def count_cars_in_image(
    image_url: str = Body(None),
    image_id: str = Body(None),
    image_binary: UploadFile = File(None),
    apply_grayscale: bool = False,
    model=Depends(get_model),
):
    if not any([image_url, image_binary, image_id]):
        raise HTTPException(
            status_code=422,
            detail={
                "field error": "At least one of the values should be provided",
                "values": {
                    "image_url": image_url,
                    "image_id": image_id,
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
        elif image_id:
            with database:
                image_path = BorderCapture.get(id=image_id).image_path
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
