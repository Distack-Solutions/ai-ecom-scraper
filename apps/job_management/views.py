from django.shortcuts import render, redirect
from django.http import HttpResponse
from .data_handler import MyOBToDjangoSync
from .models import Job
from django.core.paginator import Paginator
from django.db.models import Q, Value, CharField, F
import random
from faker import Faker
from django.utils import timezone
from .models import Assignment, Job
from apps.accounts.models import Employee
from datetime import datetime
from django.http import JsonResponse
from django.db.models.functions import Concat   
from django.conf import settings
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
TOTAL_RECORDS_LIMIT = settings.TOTAL_RECORDS_LIMIT

@login_required
def all_jobs(request):
    query = request.GET.get('q')
    all_jobs_list = Job.objects.all()

    if query:
        # Apply search filter here
        all_jobs_list = all_jobs_list.annotate(
            complete_name1=Concat('name', Value(' - '), 'number')
        )

        all_jobs_list = all_jobs_list.filter(
            Q(complete_name1__icontains=query) | 
            Q(customer__name__icontains=query)
        )


    paginator = Paginator(all_jobs_list, TOTAL_RECORDS_LIMIT)  # Change 10 to the number of items per page you desire
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'jobs': page_obj,
        'page': 'job'
    }
    return render(request, "all_jobs.html", context)

@login_required
def single_job_view(request, job_id):
    from apps.work_tracker.models import Session, Timesheet
    try:
        job = Job.objects.get(id = job_id)
    except Exception as e:
        messages.error(request, f"Job with id {job_id} does not exist.")
        return redirect("job_management:job-home")

    fields_data = {}
    exclude = ['myob_row_version', 'uri', 'myob_uid', 'is_active']
    for field in job._meta.fields:
        if field.name not in exclude:
            key = field.verbose_name
            value = getattr(job, field.name)
            fields_data[key] = value
    fields_data['status'] = job.get_status[0]


    sessions = Session.objects.filter(timesheet__assignment__job=job)
    groupview = request.GET.get('groupview')
    group_assignments = []
    if groupview == 'true':
        group_assignments = Assignment.objects.filter(job=job)

    context = {
        'group_assignments': group_assignments,
        'sessions': sessions,
        'job': job,
        'fields_data': fields_data,
        'page': 'job'

    }
    return render(request, "single-job.html", context)

def fetch_job_assignments(request):
    if not request.user.is_authenticated:
        return JsonResponse([], safe=False)
    
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')
    
    # Convert start and end date strings to datetime objects
    start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M:%S%z") if start_date_str else None
    end_date = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M:%S%z") if end_date_str else None

    assignments_queryset = Assignment.objects.all()
    if start_date and end_date:
        assignments_queryset = assignments_queryset.filter(date__range=[start_date, end_date])

    assignment_list = []
    for assignment in assignments_queryset:
        title = f'<div class="p-2"><div class="mb-2">{assignment.job.number}</div><div class="d-flex align-items-center"><i class="material-icons fs-6">person</i><span class="mx-2">{assignment.employee}</span><div></<div>'
        date = assignment.date.strftime("%Y-%m-%d")
        assignment_list.append({
            'id': assignment.id,
            'title': title,
            'date': date
        })

    return JsonResponse(assignment_list, safe=False)



def populate_assignment_model(current_user):
    fake = Faker()
    jobs = Job.objects.all()
    employees = Employee.objects.all()
    
    for _ in range(100):
        job = random.choice(jobs)
        employee = random.choice(employees)
        date = fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None)
        start_time = fake.time(pattern="%H:%M:%S", end_datetime=None)
        finish_time = fake.time(pattern="%H:%M:%S", end_datetime=None)
        while finish_time <= start_time:
            finish_time = fake.time(pattern="%H:%M:%S", end_datetime=None)
        assigned_by = current_user  # You might want to set this to a specific user if needed
        created_at = fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None)

        assignment = Assignment.objects.create(
            job=job,
            employee=employee,
            date=date,
            start_time=start_time,
            finish_time=finish_time,
            assigned_by=assigned_by,
            created_at=created_at
        )
        print(assignment)

    return 'Successfully populated Assignment model with fake data'


@login_required
def job_assignments(request):
    query = request.GET.get('q')
    all_jobs_assignment_list = Assignment.objects.all()


    if query:
        # Apply search filter here
        all_jobs_assignment_list = all_jobs_assignment_list.annotate(
            complete_job_name=Concat('job__name', Value(' - '), 'job__number'),
            full_employee_name=Concat('employee__user__first_name', Value(' '), 'employee__user__last_name'),
        )

        all_jobs_assignment_list = all_jobs_assignment_list.filter(
            Q(complete_job_name__icontains=query) | 
            Q(full_employee_name__icontains=query)
        )  

    paginator = Paginator(all_jobs_assignment_list, TOTAL_RECORDS_LIMIT)  # Change 10 to the number of items per page you desire
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'assignments': page_obj,
        'page': 'assignment'
    }


    return render(request, "job-assignments.html", context)


@login_required
def single_job_assignment(request, assignment_id):
    try:
        assignment = Assignment.objects.get(id = assignment_id)
    except Exception as e:
        messages.error(request, f"Job Assignment with id {assignment_id} does not exist.")
        return redirect("job_management:job-assignments")

    context = {
        'assignment': assignment,
        'page': 'assignment',
        'timesheet': assignment.get_timesheet(),
    }
    return render(request, "single-assignment.html", context)

@login_required
def approve_single_job_assignment(request, assignment_id):
    try:
        assignment = Assignment.objects.get(id = assignment_id)
    except Exception as e:
        messages.error(request, f"Job Assignment with id {assignment_id} does not exist.")
        return redirect("job_management:job-assignments")

    timesheet = assignment.get_timesheet()
    if timesheet:
        timesheet.status = "Approved"
        timesheet.save()
    messages.success(request, "Timesheet of this job assignment has been approved")
    return redirect("job_management:single-job-assignment", assignment_id=assignment_id)

@login_required
def create_job_assignments(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            new_assignment = Assignment(**form.cleaned_data, assigned_by=request.user)
            new_assignment.save()
            messages.success(request, "Job has been assigned successfully")
            
            if request.POST.get('action') == 'save':
                return redirect('job_management:job-assignments')
            elif request.POST.get('action') == 'save_and_add_another':
                return redirect('job_management:create-job-assignments')
                # Optionally, you can add a success message here
    else:
        form = AssignmentForm(initial={
            'job':request.GET.get('job'),
            'employee':request.GET.get('employee'),
            'date': request.GET.get('date')
        })
    
    context = {
        'page': 'assignment',
        'form': form
    }
    return render(request, "create-job-assignment.html", context)



def search_job(request):
    if not request.user.is_authenticated:
        return JsonResponse([], safe=False)
    
    if 'term' in request.GET:
        term = request.GET.get('term')
        print(term, 'wow')
        if term and len(term) < 2:
            return JsonResponse([], safe=False)

        # Apply search filter here
        all_jobs_list = Job.objects.annotate(
            complete_name1=Concat('name', Value(' - '), 'number')
        ).filter(complete_name1__icontains=term)
        results = [{'id': job.id, 'text': str(job)} for job in all_jobs_list]
        return JsonResponse(results, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)