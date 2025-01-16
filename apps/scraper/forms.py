from django import forms
from .models import ScrapingProcess, SourceWebsite

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



class ProductFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title...',
            'onkeyup': 'document.getElementById("filter-form").submit()',
        })
    )
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('all', 'All'),
            ('draft', 'Draft'),
            ('under_review', 'Under Review'),
            ('declined', 'Declined'),
            ('approved', 'Approved'),
            ('published', 'Published'),
            ('archived', 'Archived')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'document.getElementById("filter-form").submit()',
        })
    )
    marketplace = forms.ChoiceField(
        required=False,
        choices=[],  # We'll populate this dynamically in the view
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'document.getElementById("filter-form").submit()',
        })
    )
    per_page = forms.ChoiceField(
        required=False,
        choices=[(10, '10'), (20, '20'), (50, '50'), (100, '100')],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'document.getElementById("filter-form").submit()',
        })
    )

    def __init__(self, *args, **kwargs):
        # Dynamically populate the marketplace choices
        super().__init__(*args, **kwargs)
        self.fields['marketplace'].choices = [('all', 'All')] + [
            (website.name, website.name) for website in SourceWebsite.objects.all()
        ]
