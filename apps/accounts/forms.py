from django.contrib.auth.forms import SetPasswordForm, UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy

class EditProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set a custom link for the password field
        change_password_link = reverse_lazy('accounts:change-profile-password') 
        self.fields['password'].help_text = f'Raw passwords are not stored, so there is no way to see password, but you can change the password using <a href="{change_password_link}" class="bg-secondary rounded p-1 text-white">This form</a>.'

class AdminSetPasswordForm(SetPasswordForm):
    pass
