from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plaid_rest_celery.settings')

plaid_app = Celery('plaid_rest_celery')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
plaid_app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
plaid_app.autodiscover_tasks()


@plaid_app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
