# Get current working directory
HOME=$(pwd)
# Set the URL
URL='https://frame.pkpd.lt/lt/border/stream/checkpoint.sumskas/video.sumskas'
# Get fetch interval variable
MIN=$FETCH_INTERVAL
# Create the cron job
(
  # Retrieve environment variables
  printenv | grep "POSTGRES\|RABBIT\|\IMAGE"
  # Set cron HOME working directory
  echo HOME=${HOME}
  echo URL=${URL}
  echo "*/${MIN} * * * * $(which python3) main.py >> logs.log 2>&1"
) | crontab -