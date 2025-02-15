from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.decorators import method_decorator
# from apps.customer_management.forms import *
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
import json
from .models import Customer, Employee
from django.core.paginator import Paginator
from django.db.models.functions import Concat   
from django.db.models import Value
from django.conf import settings
from apps.job_management.forms import AssignmentForm
from django.http import JsonResponse
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.models import User
from django.http import Http404
from .forms import *
from apps.scraper.models import Product
from apps.ai.models import OpenAIAPIUsage
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from apps.scraper.models import ScrapingProcess

TOTAL_RECORDS_LIMIT = settings.TOTAL_RECORDS_LIMIT


@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            user = form.save()
            messages.success(request, "Profile has been updated successfully")
            return redirect('accounts:profile')
    else:
        form = EditProfileForm(instance=user)

    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'edit_profile.html', context)




class CustomCurrentUserPasswordChangeView(PasswordChangeView):
    template_name = 'change_profile_password.html'  # Create this template
    form_class = AdminSetPasswordForm
    
    def get_success_url(self):
        return reverse_lazy('accounts:profile')  # Update with your profile URL

    def form_valid(self, form):
        self.request.user.set_password(form.cleaned_data['new_password1'])
        self.request.user.save()

        messages.success(self.request, 'Password successfully changed.')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Failed to change password. Please correct the errors.')
        return super().form_invalid(form)



@login_required
def my_profile(request):
    user = request.user
    fields_data = {}
    exclude = ['password', 'is_active', 'is_deleted', 'is_superuser', 'is_admin', 'is_staff', 'profile_picture', 'is_staff']
    for field in user._meta.fields:
        if field.name not in exclude:
            key = field.verbose_name
            value = getattr(user, field.name)
            fields_data[key] = value

    context = {
        'fields_data': fields_data
    }
    return render(request, "myprofile.html", context)



@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class EmployeePasswordChangeView(PasswordChangeView):
    template_name = 'employees/change-employee-password.html'  # Create this template
    form_class = AdminSetPasswordForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.kwargs['id']
        context['myuser'], context['employee'] = self.get_user()
        return context

    def get_success_url(self):
        return reverse_lazy('accounts:single-employee', kwargs={'employee_id': self.kwargs['id']})

    def get_user(self):
        id = self.kwargs['id']
        employee = get_object_or_404(Employee, pk=id)
        return employee.user, employee

    def form_valid(self, form):
        user, employee = self.get_user()
        new_password = form.cleaned_data['new_password1']

        # Set the new password for the specified user
        user.set_password(new_password)
        user.save()

        messages.success(self.request, 'Password successfully changed.')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Failed to change password. Please correct the errors.')
        return super().form_invalid(form)
    
    def dispatch(self, request, *args, **kwargs):
        try:
            self.get_user()
        except Http404:
            id = self.kwargs['id']
            messages.error(request, "Employee with ID {} does not exist.".format(id))
            return redirect("accounts:home")
        return super().dispatch(request, *args, **kwargs)




def search_employee(request):
    if not request.user.is_authenticated:
        return JsonResponse([], safe=False)
    
    if 'term' in request.GET:
        term = request.GET.get('term')
        if term and len(term) < 2:
            return JsonResponse([], safe=False)

        # Apply search filter here
        all_jobs_list = Employee.objects.annotate(
            full_name = Concat('user__first_name', Value(' '), 'user__last_name')
        ).filter(full_name__icontains=term)

        results = [{'id': employee.id, 'text': str(employee)} for employee in all_jobs_list]
        return JsonResponse(results, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)




# Django view
@login_required
def settings_view(request):
    config_form = ConfigForm()
    wc_config_form = WoocommerceConfigForm()

    if request.method == "POST":
        form_type = request.POST.get('form_type')
        if form_type == 'openai_config':
            config_form = ConfigForm(request.POST)
            if config_form.is_valid():
                config_form.save()
                messages.success(request, "OpenAI configuration updated successfully.")
                return redirect('accounts:settings')
        else:
            wc_config_form = WoocommerceConfigForm(request.POST)
            if wc_config_form.is_valid():
                wc_config_form.save()
                messages.success(request, "WooCommerce configuration updated successfully.")
                return redirect('accounts:settings')

    context = {
        'config_form': config_form,
        'wc_config_form': wc_config_form,
        'page': 'settings'
    }
    return render(request, "volt/settings.html", context)



@login_required
def home_view(request):
    total_days = 10

    # Calculate date range
    start_date = (timezone.now() - timedelta(days=total_days)).date()
    end_date = timezone.now().date()  # Explicitly get today's date

    # Aggregate product counts
    stats = Product.objects.aggregate(
        total=Count('id'),
        published=Count('id', filter=Q(status='published')),
        declined=Count('id', filter=Q(status='declined')),
    )

    # Get daily counts for products
    daily_counts = (
        Product.objects.filter(created_at__date__gte=start_date)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    labels = [(start_date + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(total_days)]
    print(labels)
    data = [0] * total_days

    for entry in daily_counts:
        entry_date = entry['date'].strftime('%Y-%m-%d')
        if entry_date in labels:
            date_index = labels.index(entry_date)
            data[date_index] = entry['count']

    product_graph_data = {
        'labels': labels,
        'data': data,
    }

    # Get OpenAI API usage data
    openai_daily_usage = (
        OpenAIAPIUsage.objects.filter(request_timestamp__date__gte=start_date)
        .annotate(date=TruncDate('request_timestamp'))
        .values('date')
        .annotate(
            total_tokens=Sum('total_tokens'),
            prompt_tokens=Sum('prompt_tokens'),
            completion_tokens=Sum('completion_tokens'),
            response_count=Count('*')  # Count the total number of requests (objects)
        )
        .order_by('date')
    )

    openai_data = {label: {'total': 0, 'prompt': 0, 'completion': 0, 'response_count': 0} for label in labels}

    for usage in openai_daily_usage:
        entry_date = usage['date'].strftime('%Y-%m-%d')
        if entry_date in openai_data:
            openai_data[entry_date] = {
                'total': usage['total_tokens'],
                'prompt': usage['prompt_tokens'],
                'completion': usage['completion_tokens'],
                'response_count': usage['response_count'],
            }

    # Populate OpenAI graph data
    openai_graph_data = {
        'labels': labels,
        'total_tokens': [openai_data[date]['total'] for date in labels],
        'prompt_tokens': [openai_data[date]['prompt'] for date in labels],
        'completion_tokens': [openai_data[date]['completion'] for date in labels],
        'response_count': [openai_data[date]['response_count'] for date in labels],
    }

    # code to caclulate success ratio of Process
    success_ratio = 0
    total_scraping_process = ScrapingProcess.objects.all().count()
    if total_scraping_process > 0:
        completed_scraping_process = ScrapingProcess.objects.filter(status='completed').count()
        success_ratio = completed_scraping_process / total_scraping_process * 100
        success_ratio = f'{round(success_ratio, 0)}% ({completed_scraping_process})'

    context = {
        'total_openai_requests': OpenAIAPIUsage.objects.all().count(),
        'all_scraping_process': total_scraping_process,
        'scraping_success_ratio': success_ratio,
        'page': 'dashboard',
        'total_products': stats['total'],
        'published_products': stats['published'],
        'declined_products': stats['declined'],
        'graph_data': product_graph_data,
        'openai_graph_data': openai_graph_data,
    }
    return render(request, "volt/dashboard.html", context)


@login_required
def process_monitoring(request):
    return render(request, "volt/process_monitoring.html", )
@login_required
def initiate_process(request):
    return render(request, "volt/initiate_process.html", )

@login_required
def product_detail(request):
    return render(request, "volt/product_detail.html", )

@login_required
def product(request):
    return render(request, "volt/product.html", )

@login_required
def signin(request):
    return render(request, "volt/signin.html", )
    


@login_required
def all_customers_view(request):
    query = request.GET.get('q')
    all_customers_list = Customer.objects.all()
    if query:
        all_customers_list = all_customers_list.filter(name__icontains=query)

    paginator = Paginator(all_customers_list, TOTAL_RECORDS_LIMIT)  # Change 10 to the number of items per page you desire
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'customers': page_obj,
        'page': 'customer'

    }
    return render(request, "customers/all-customers.html", context)

@login_required
def single_customer_view(request, customer_id):
    try:
        customer = Customer.objects.get(id = customer_id)
    except Exception as e:
        messages.error(request, f"Customer with id {customer_id} does not exist.")
        return redirect("accounts:all-customers")
    fields_data = {}
    exclude = ['myob_row_version', 'uri', 'myob_uid', 'is_active']
    for field in customer._meta.fields:
        if field.name not in exclude:
            key = field.verbose_name
            value = getattr(customer, field.name)
            fields_data[key] = value
    fields_data['status'] = "Active" if customer.is_active else "Inactive"

    context = {
        'customer': customer,
        'fields_data': fields_data,
        'page': 'customer'

    }
    return render(request, "customers/single-customer.html", context)

@login_required
def all_employees_view(request):
    all_employees_list = Employee.objects.all()
    query = request.GET.get('q')
    if query:
        all_employees_list = all_employees_list.annotate(full_name = Concat('user__first_name', Value(' '), 'user__last_name'))
        all_employees_list = all_employees_list.filter(full_name__icontains=query)


    paginator = Paginator(all_employees_list, TOTAL_RECORDS_LIMIT)  # Change 10 to the number of items per page you desire
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'employees': page_obj,
        'page': 'employee'

    }
    return render(request, "employees/all-employees.html", context)

@login_required
def single_employee_view(request, employee_id):
    try:
        employee = Employee.objects.get(id = employee_id)
    except Exception as e:
        messages.error(request, f"Employee with id {employee_id} does not exist.")
        return redirect("accounts:all-employees")
    fields_data = {}
    exclude = ['myob_row_version', 'uri', 'myob_uid', 'is_active']
    for field in employee._meta.fields:
        if field.name not in exclude:
            print(field.name)
            key = field.verbose_name
            value = getattr(employee, field.name)
            fields_data[key] = value
    fields_data['status'] = "Active" if employee.is_active else "Inactive"

    context = {
        'employee': employee,
        'fields_data': fields_data,
        'page': 'employee'

    }
    return render(request, "employees/single-employee.html", context)




def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:home")
    
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_path = request.POST.get("next")
            
            messages.success(request, "You've been logged successfully.")
            if next_path:
                return redirect(next_path)
            

            return redirect('accounts:home')
    else:
        form = AuthenticationForm()
    return render(request, 'volt/signin.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')





# Error handler

def custom_permission_denied(request, exception):
    return render(request, '403.html', status=403)