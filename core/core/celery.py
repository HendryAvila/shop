import os
from celery import Celery
from celery.signals import worker_process_init

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Create the Celery application
app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Windows specific configuration
app.conf.update(
    broker_connection_retry_on_startup=True,
    worker_pool_restarts=True,
    task_track_started=True,
    worker_max_tasks_per_child=1,  # Restart worker processes after each task
)

# Load task modules from all registered Django apps
app.autodiscover_tasks()

@worker_process_init.connect
def worker_process_init_handler(**_):
    # Reset connection on worker startup
    from django.db import connections
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
