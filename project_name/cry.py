# Celery Application
# https://docs.celeryq.dev/en/stable/

import os
import celery

from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{project_name}}.settings")

celery_app = celery.Celery(
    main="{{project_name}}",
    namespace="{{project_name}}|celery",
    changes=settings.CELERY,
    # config_source=settings.CELERY
)
celery_app.autodiscover_tasks()
