from django import forms
from apps.job_management.models import Job
from apps.accounts.models import Employee
from django.utils.safestring import mark_safe


class FilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'Select Status'),
        ('all', 'All'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]

    
    from_date = forms.DateField(label='Start Date', required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'filters'}))
    to_date = forms.DateField(label='End Date', required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'filters'}))
    status = forms.ChoiceField(label='Status', choices=STATUS_CHOICES, required=False, widget=forms.Select(attrs={'class': 'filters select2'}))
    job = forms.ModelChoiceField(
        queryset=Job.objects.none(), 
        widget=forms.Select(attrs={'class': 'select2 job-select filters'}), 
        required=False
    )
    employee = forms.ModelChoiceField(queryset=Employee.objects.none(), widget=forms.Select(attrs={'class': 'select2 employee-select filters'}), required=False)

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        initials = kwargs.get('initial', {})
        initial_job = initials.get('job')
        initial_employee = initials.get('employee')
        if initial_job:
            self.fields['job'].queryset = Job.objects.filter(id=initial_job)
        
        if initial_employee:
            self.fields['employee'].queryset = Employee.objects.filter(id=initial_employee)
