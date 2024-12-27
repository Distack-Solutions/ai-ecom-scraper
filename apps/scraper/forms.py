from django import forms
from .models import ScrapingProcess

class ScrapingProcessForm(forms.ModelForm):
    class Meta:
        model = ScrapingProcess
        fields = ['search_query', 'source_websites', 'criterias', 'max_records']  # Fields to include in the form
        widgets = {
            'source_websites': forms.CheckboxSelectMultiple(),  # For multiple selections of source websites
            'criterias': forms.CheckboxSelectMultiple(),  # For multiple selections of criteria
        }


    # Optionally, add validation or custom methods here, for example:
    def clean_max_records(self):
        max_records = self.cleaned_data.get('max_records')
        if max_records <= 0:
            raise forms.ValidationError("Max records must be a positive integer.")
        return max_records
