from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Session
from django.utils import timezone
from django.db.models import Sum, F

@receiver(post_save, sender=Session)
def update_timesheet_duration(sender, instance, created, **kwargs):
    if instance.duration:
        timesheet = instance.timesheet
        total_duration = Session.objects.filter(
            timesheet=timesheet, end_time__isnull=False
        ).aggregate(total_duration=Sum(F('duration')))['total_duration'] or timezone.timedelta()

        timesheet.duration = total_duration
        timesheet.hours_worked = total_duration.total_seconds() / 3600
        timesheet.save()