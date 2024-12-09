from django.db import models
from django.contrib.auth.models import User


def global_format_duration(duration_object):
    if duration_object:
        days = duration_object.days
        hours, remainder = divmod(duration_object.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []

        if hours:
            if days:
                hours += (days * 24)
            parts.append(f"{hours} hr{'s' if hours != 1 else ''}")
        if minutes:
            parts.append(f"{minutes} min{'s' if minutes != 1 else ''}")
        if seconds:
            parts.append(f"{seconds} sec{'s' if seconds != 1 else ''}")

        return ' '.join(parts)
    else:
        return "Not specified"


# Create your models here.
class Timesheet(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPROVE = "Approved", "Approved"

    assignment = models.OneToOneField('job_management.Assignment', on_delete=models.CASCADE, related_name="timesheet")
    duration = models.DurationField(null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_duration(self):
        return global_format_duration(self.duration)

    def get_sessions(self):
        return self.session_set.all()

    def __str__(self):
        return f"Timesheet for {self.assignment}"



class Session(models.Model):
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    clock_on_location = models.JSONField(null=True, blank=True)
    clock_off_location = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @staticmethod
    def format_duration(duration_object):
        return global_format_duration(duration_object)

    def get_duration(self):
        return self.format_duration(self.duration)

    class Meta:
        ordering = ("-id",)

    def save(self, *args, **kwargs):
        # Calculate duration before saving
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Session for Timesheet {self.timesheet_id} ({self.start_time} to {self.end_time})"

