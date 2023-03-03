import torch
from enum import Enum


class Yolov5(str, Enum):
    """YOLOv5 available model distribution/size names."""

    nano = "yolov5n"
    small = "yolov5s"
    medium = "yolov5m"
    large = "yolov5l"
    extra = "yolov5x"


if __name__ == "__main__":
    # Download pretrained models and save in current directory

    for model_size in Yolov5:
        torch.hub.load(
            model=model_size,
            repo_or_dir="ultralytics/yolov5",
            source="github",
            pretrained=True,
            force_reload=False,
        )
