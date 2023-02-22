# Get current working directory
HOME=$(pwd)
# Get fetch interval variable
MIN=$FETCH_INTERVAL
# Create the cron job
(
  # Retrieve environment variables
  printenv | grep "POSTGRES\|RABBIT\|\IMAGE"
  # Set cron HOME working directory
  echo HOME=${HOME}
  while IFS=, read -r URL URL_LOCATION; do
    echo URL=${URL}
    echo URL_LOCATION=${URL_LOCATION}
    echo "*/${MIN} * * * * $(which python3) main.py >> logs.log 2>&1"
  done < urls.csv
) | crontab -