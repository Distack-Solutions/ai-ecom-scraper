from django.urls import path
from . import views
from django.views.i18n import set_language

app_name = "work_tracker"

urlpatterns = [
    # path('jobs', views.all_jobs, name='job_home'),
    path('timesheet/', views.timesheet, name='timesheet')
]
