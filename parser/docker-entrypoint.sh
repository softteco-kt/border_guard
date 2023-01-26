#!/bin/bash

# Setup cron with crontab
sh setup_cron.sh

# Create tables
python3 models.py

# Redirecting output of non pid 1 process to docker logs
tail -n 0 -q -F /usr/src/parser/*.log >> /proc/1/fd/1 &

# Run cron as main process
cron -f