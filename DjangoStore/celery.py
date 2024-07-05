import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoStore.settings.dev")

celery = Celery("DjangoStore")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
celery.config_from_object(f"django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
celery.autodiscover_tasks()
