# Automatic peewee model generator
python -m pwiz -f -e postgres \
    --host $POSTGRES_HOST \
    --port $POSTGRES_PORT \
    --password $POSTGRES_PASSWORD \
    --user $POSTGRES_USER $POSTGRES_DATABASE \
    -i -o > auto_generated_models.py
