from functools import lru_cache
from io import BytesIO

import torch

from fastapi import Body, Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache
def get_model():
    return torch.hub.load(
        "ultralytics/yolov5", "yolov5n", pretrained=True, force_reload=False
    )


@app.on_event("startup")
def startup():
    get_model()


class CarsMetaData(BaseModel):
    amount: int


@app.post("/cars_on_border", response_model=CarsMetaData)
async def count_cars_in_image(
    image_url: str = Body(None),
    image_binary: UploadFile = File(None),
    model=Depends(get_model),
):
    # decode + process image with PIL
    if not any([image_url, image_binary]):
        raise HTTPException(
            status_code=422,
            detail={
                "field error": "At least one of the values should be provided",
            },
        )

    if image_binary:
        result = model(Image.open(BytesIO(await image_binary.read())))
        return count_cars(result, model)
    else:
        raise HTTPException(status_code=501, detail={"error": "Not Implemented."})


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
