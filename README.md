```sh
# Make sure to have poetry installed
poetry --version

# Export ENV variables
export URL=<URL HERE>

# Setup project
source setup.sh
# Install poetry and dependencies
make install
# Provide URL in env variables and run
make run

# For server setup 
# add URL to cron.env ->
make run-cron
```
