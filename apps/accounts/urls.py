from django.urls import path
from . import views
from django.views.i18n import set_language
from django.contrib.auth.decorators import login_required

app_name = "accounts"

urlpatterns = [
    path('', views.home_view, name='home'),
    path('accounts/profile/', views.my_profile, name='profile'),
    path(
        'accounts/profile/change-password', 
        login_required(views.CustomCurrentUserPasswordChangeView.as_view()),
        name='change-profile-password'
    ),
    path('accounts/profile/edit', views.edit_profile, name='edit-profile'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),

    path('accounts/customers', views.all_customers_view, name='all-customers'),
    path('accounts/customers/<customer_id>/view', views.single_customer_view, name='single-customer'),

    path('accounts/employees', views.all_employees_view, name='all-employees'),
    path('accounts/employees/<employee_id>/view', views.single_employee_view, name='single-employee'),

    path(
        'accounts/employees/<id>/change-password', 
        login_required(views.EmployeePasswordChangeView.as_view()),
        name='change-employee-password'
    ),

    path('employees/search_employee', views.search_employee, name='search_employee'),


]
