from celery import Celery

app = Celery('worker')
# Celery configuration
app.config_from_object('celeryconfig')