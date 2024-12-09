from django import forms
from .models import Assignment, Job
from apps.accounts.models import Employee
from django.core.exceptions import ValidationError


class AssignmentForm(forms.ModelForm):
    job = forms.ModelChoiceField(queryset=Job.objects.none(), widget=forms.Select(attrs={'class': 'select2 job-select'}))
    employee = forms.ModelChoiceField(queryset=Employee.objects.none(), widget=forms.Select(attrs={'class': 'select2 employee-select'}))


    class Meta:
        model = Assignment
        exclude = ['roster', 'plant', 'created_at', 'assigned_by']
    

    def __init__(self, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)
        
        # Check if initial values are provided for job and employee fields
        initials = kwargs.get('initial', {})
        initial_job = initials.get('job')
        initial_employee = initials.get('employee')
        # Access the provided data
        provided_data = self.data
        given_job = provided_data.get('job')
        given_employee = provided_data.get('employee')

        # Set queryset for job field based on initial value
        if initial_job:
            self.fields['job'].queryset = Job.objects.filter(id = initial_job)  # Assuming Job is the related model
            
        # Set queryset for employee field based on initial value
        if initial_employee:
            self.fields['employee'].queryset = Employee.objects.filter(id = initial_employee)  # Assuming Employee is the related model

        # Set queryset for job field based on initial value
        if given_job:
            self.fields['job'].queryset = Job.objects.filter(id = given_job)  # Assuming Job is the related model
            
        # Set queryset for employee field based on initial value
        if given_employee:
            self.fields['employee'].queryset = Employee.objects.filter(id = given_employee)  # Assuming Employee is the related model

        