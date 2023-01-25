# Get the current working directory
HOME=$(pwd)
# Set the URL
URL='https://frame.pkpd.lt/lt/border/stream/checkpoint.sumskas/video.sumskas'
# Create the cron job
(
  echo HOME=${HOME}
  echo URL=${URL}
  echo "* * * * * $(which python3) main.py >> logs.log 2>&1"
) | crontab -