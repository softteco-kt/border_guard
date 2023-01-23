## A simple parser service

Workflow:

- Downloads an image from given URL address ->
- Writes the image to disk ->
- Saves image metadata to database ->
- Sends image_id to message queue for further processing.
