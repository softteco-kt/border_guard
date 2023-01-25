#!/bin/bash

# Setup cron with crontab
sh setup_cron.sh

# Create tables
python3 models.py

# Run cron as main process
cron -f