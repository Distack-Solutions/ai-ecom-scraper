from django.db import models
from apps.accounts.models import Customer, Address
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db.models import Q
from django.db.models import Value, CharField
# Create your models here.

# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver


class Check(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(
        help_text="Enter the check description here.", blank=True, null=True
    )


class CheckList(models.Model):
    checks = models.ManyToManyField(Check)
    name = models.CharField(max_length=255)

    def __str__(self):
        """Return the name of the checklist."""
        return self.name



class Job(models.Model):
    class Status(models.TextChoices):
        NOT_INITIATED = "Not Initiated", "Not Initiated"
        PENDING = "Pending", "Pending"
        COMPLETE = "Complete", "Complete"
        IMMEDIATE_ACTION = "Immediate Action", "Immediate Action"

    display_id = models.CharField(max_length=255, null=True, blank=True)
    myob_uid = models.CharField(unique=True, max_length=50, null=True, blank=True)
    myob_row_version = models.BigIntegerField(null=True, blank=True)
    
    name = models.CharField(max_length=50)
    number = models.CharField(max_length=30)
    description = models.TextField(null=True, blank=True, default="No description is provided.")
    parent_job = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_INITIATED, blank=True)
    is_active = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateTimeField(null=True, blank=True)
    last_modified_date = models.DateTimeField(null=True, blank=True)
    checklist = models.ForeignKey(CheckList, on_delete=models.SET_NULL, null=True, blank=True)

    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True, blank=True, null=True)
    uri = models.URLField(null=True, blank=True)

    @property
    def get_status(self):
        status_dictionary = {
            "NI": ("Not Initiated", "secondary"),
            "PN": ("Pending", "warning"),
            "CP": ("Complete", "success"),
            "IA": ("Immediate Action", "danger"),
            "Not Initiated": ("Not Initiated", "secondary"),
            "Pending": ("Pending", "warning"),
            "Complete": ("Complete", "success"),
            "Immediate Action": ("Immediate Action", "danger")
        }
        return status_dictionary[self.status]

    @property
    def complete_name(self):
        return f"{self.name} - {self.number}"

    def get_assignments(self):
        return Assignment.objects.filter(job = self)

    def __str__(self):
        return self.complete_name




class Roster(models.Model):
    name = models.CharField(max_length = 255, null=True, blank=True)
    start_date = models.DateField(null=True)
    finish_date = models.DateField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("start_date", "finish_date")

    def __str__(self):
        return f'{self.start_date}  to  {self.finish_date}'


class Plant(models.Model):
    number = models.CharField(max_length=10)
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.number} - {self.description}"


class Assignment(models.Model):
    roster = models.ForeignKey(Roster, on_delete=models.SET_NULL, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    employee = models.ForeignKey('accounts.Employee', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    finish_time = models.TimeField(blank=True, null=True)
    plant = models.ForeignKey(
        Plant, on_delete=models.SET_NULL, null=True, blank=True
    )
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.job} -> {self.employee}'


    def get_timesheet(self):
        if hasattr(self, 'timesheet'):
            return self.timesheet
        return None

    class Meta:
        ordering = ('-created_at',)