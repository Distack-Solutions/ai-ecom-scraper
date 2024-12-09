from django.urls import path
from . import views
from django.views.i18n import set_language

app_name = "job_management"

urlpatterns = [
    # path('jobs', views.all_jobs, name='job_home'),
    path('jobs/', views.all_jobs, name='job-home'),
    path('jobs/<job_id>/view', views.single_job_view, name='single-job'),
    

    path('jobs/assignments', views.job_assignments, name='job-assignments'),
    path('jobs/assignments/<assignment_id>/view', views.single_job_assignment, name='single-job-assignment'),
    path('jobs/assignments/<assignment_id>/approve', views.approve_single_job_assignment, name='approve-job-assignment'),



    path('jobs/assignments/create', views.create_job_assignments, name='create-job-assignments'),
    path('jobs/assignments/fetch', views.fetch_job_assignments, name='fetch-job-assignments'),

    path('jobs/search_job', views.search_job, name='search_job'),

]
