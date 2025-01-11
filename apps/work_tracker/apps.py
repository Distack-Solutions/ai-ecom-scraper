from django.apps import AppConfig


class WorkTrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.work_tracker'
    verbose_name = 'Work Tracker'

    def ready(self):
        import apps.work_tracker.signals