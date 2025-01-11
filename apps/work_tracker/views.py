from django.shortcuts import render
from .models import Session, Timesheet
from django.core.paginator import Paginator
from django.db.models import Q
from apps.job_management.models import Job, Assignment
from apps.accounts.models import Employee
from django.utils import timezone
from datetime import datetime, timedelta
from faker import Faker
import random
from django.db.models import Sum, F
from django.conf import settings
from django.contrib.auth.models import User
from .form import FilterForm
from django.contrib.auth.decorators import login_required
TOTAL_RECORDS_LIMIT = settings.TOTAL_RECORDS_LIMIT


def generate_fake_sessions():
    fake = Faker()

    # Get all timesheets
    assignments = Assignment.objects.all()

    # Generate fake sessions
    sessions = []
    for _ in range(200):
        # Choose a random timesheet
        assignment = random.choice(assignments)
        timesheet, created = Timesheet.objects.get_or_create(assignment=assignment)


        # Generate start_time and end_time
        start_time = fake.date_time_between(start_date="-1y", end_date="now", tzinfo=None)
        end_time = start_time + timedelta(hours=random.randint(1, 8))  # Ensure end_time is ahead of start_time

        # Create session object
        session = Session(
            timesheet=timesheet,
            start_time=start_time,
            end_time=end_time
        )
        session.save()







# Create your views here.
@login_required
def timesheet(request):
    # Retrieve filter parameters from the request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    job_id = request.GET.get('job')
    employee_id = request.GET.get('employee')
    status = request.GET.get('status')
    initial_data = {
        'from_date': from_date,
        'to_date': to_date,
        'status': status,
        'job': job_id,
        'employee': employee_id,
    }

    # Initialize the form with the extracted data
    filter_form = FilterForm(initial=initial_data)
    
    sessions = Session.objects.all()
    # Apply date filter if provided
    if from_date:
        sessions = sessions.filter(end_time__date__gte=from_date)
    
    if to_date:
        sessions = sessions.filter(end_time__date__lte=to_date)

    # Apply job filter if provided
    if job_id:
        sessions = sessions.filter(timesheet__assignment__job_id=job_id)

    # Apply employee filter if provided
    if employee_id:
        sessions = sessions.filter(timesheet__assignment__employee_id=employee_id)

    # Apply status filter if provided
    if status and status!="all":
        status = status.capitalize()
        sessions = sessions.filter(timesheet__status=status)

    all_ended_sessions = sessions.filter(end_time__isnull=False)

    total_duration = all_ended_sessions.aggregate(total_duration=Sum(F('duration')))['total_duration'] or timezone.timedelta()
    total_duration = Session.format_duration(total_duration)

    total_sessions_count = sessions.count()
    total_pending_count = sessions.filter(timesheet__status='Pending').count()
    total_approved_count = sessions.filter(timesheet__status='Approved').count()
     
    paginator = Paginator(sessions, TOTAL_RECORDS_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if total_sessions_count > 0:
        approved_session_percentage = f'{round(total_approved_count/total_sessions_count*100, 0)}% ({total_approved_count} out of {total_sessions_count})'
    else:
        approved_session_percentage = '0%'
    context = {
        'sessions': page_obj,
        'total_duration': total_duration,
        'total_sessions_count': total_sessions_count,
        'total_pending_count': total_pending_count,
        'total_approved_count': total_approved_count,
        'approved_session_percentage': approved_session_percentage,
        'page': 'timesheet',
        'filter_form': filter_form
    }
    return render(request, "timesheet.html", context)


