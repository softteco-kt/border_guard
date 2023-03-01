#!/bin/bash

# Setup folders for different cameras
python3 check_folders.py

# Setup cron with crontab
( python3 setup_cron.py ) | crontab -

# Redirecting output of non pid 1 process to docker logs
tail -n 0 -q -F /usr/src/parser/*.log >> /proc/1/fd/1 &

# Run cron as main process
cron -f