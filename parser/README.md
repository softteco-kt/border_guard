## A simple parser service

Workflow:

- Downloads an image from given URL address ->
- Writes the image to disk ->
- Saves image metadata to database ->
- Sends image_id to message queue for further processing.

```sh
# Setup project
source setup.sh
# export URL and run
make run

# For server setup 
make server-setup
# To init cron job
make run-cron
```
