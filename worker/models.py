import datetime
import os
import uuid

import peewee as pw

POSTGRES_DATABASE = os.environ.get("POSTGRES_DATABASE")
POSTGRES_USERNAME = os.environ.get("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")

# Connect to a Postgres database.
database = pw.PostgresqlDatabase(
    POSTGRES_DATABASE,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    user=POSTGRES_USERNAME,
    password=POSTGRES_PASSWORD,
    autoconnect=False,
)


class BaseModel(pw.Model):
    id = pw.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = pw.TimestampField(default=datetime.datetime.now().timestamp)

    class Meta:
        database = database


class BorderCapture(BaseModel):
    number_of_cars = pw.IntegerField(null=True)
    image_path = pw.CharField(unique=True)
    processed = pw.BooleanField(default=False)


# one-to-many bounding boxes to border image instances, can have multiple bounding boxes
# accessible as as a special attribute, BorderCapture.bboxes
class AxisAlignedBoundingBoxNorm(BaseModel):
    border = pw.ForeignKeyField(BorderCapture, backref="bboxes")

    x_origin = pw.FloatField()
    y_origin = pw.FloatField()
    width = pw.FloatField()
    height = pw.FloatField()

    class Meta:
        # As the data is normalized, coordinates should be in range between 0 - 1
        constraints = [
            pw.Check("{0} <= 1 and {0} >= 0".format("x_origin")),
            pw.Check("{0} <= 1 and {0} >= 0".format("y_origin")),
            pw.Check("{0} <= 1 and {0} >= 0".format("width")),
            pw.Check("{0} <= 1 and {0} >= 0".format("height")),
        ]
