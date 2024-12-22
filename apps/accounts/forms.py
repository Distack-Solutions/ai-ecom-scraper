from django.contrib.auth.forms import SetPasswordForm, UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
import os
import json
from django import forms
from django.conf import settings


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


# Path to the configuration file
# Path to the configuration file
CONFIG_FILE = os.path.join(settings.BASE_DIR, "config.json") 
WC_CONFIG_FILE = os.path.join(settings.BASE_DIR, "wc_config.json")

class ConfigForm(forms.Form):
    api_key = forms.CharField(label="API Key", max_length=255, required=False)
    prompt = forms.CharField(label="Prompt", widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = self.get_config()
        self.fields['api_key'].initial = config.get('api_key', '')
        self.fields['prompt'].initial = config.get('prompt', '')

    @staticmethod
    def get_config():
        """Reads the configuration file or creates it with default values."""
        DEFAULT_DATA = {"api_key": "", "prompt": ""}
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "w") as file:
                json.dump(DEFAULT_DATA, file)

        with open(CONFIG_FILE, "r") as file:
            try:
                return json.load(file)
            except Exception as e:
                return DEFAULT_DATA

    def clean_prompt(self):
        """
        Validates the prompt field to ensure required placeholders are present.
        """
        prompt = self.cleaned_data.get('prompt', '')
        required_placeholders = ["{product_title}", "{product_description}", "{category}", "{source_website_name}"]

        missing_placeholders = [placeholder for placeholder in required_placeholders if placeholder not in prompt]

        if missing_placeholders:
            raise forms.ValidationError(
                f"The prompt is missing the following required placeholders: {', '.join(missing_placeholders)}"
            )

        return prompt

    def save(self):
        """Saves the form data to the configuration file."""
        config = {
            "api_key": self.cleaned_data.get("api_key", ""),
            "prompt": self.cleaned_data.get("prompt", "")
        }
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file)


class WoocommerceConfigForm(forms.Form):
    store_url = forms.URLField(label="Store URL", max_length=255, required=True)
    consumer_key = forms.CharField(label="Consumer Key", max_length=255, required=True)
    consumer_secret = forms.CharField(label="Consumer Secret", max_length=255, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = self.get_config()
        self.fields['store_url'].initial = config.get('store_url', '')
        self.fields['consumer_key'].initial = config.get('consumer_key', '')
        self.fields['consumer_secret'].initial = config.get('consumer_secret', '')

    @staticmethod
    def get_config():
        """Reads the WooCommerce configuration file or creates it with default values."""
        DEFAULT_DATA = {"store_url": "", "consumer_key": "", "consumer_secret": ""}
        if not os.path.exists(WC_CONFIG_FILE):
            with open(WC_CONFIG_FILE, "w") as file:
                json.dump(DEFAULT_DATA, file)

        with open(WC_CONFIG_FILE, "r") as file:
            try:
                return json.load(file)
            except Exception as e:
                return DEFAULT_DATA

    def save(self):
        """Saves the WooCommerce configuration data to the file."""
        config = {
            "store_url": self.cleaned_data.get("store_url", ""),
            "consumer_key": self.cleaned_data.get("consumer_key", ""),
            "consumer_secret": self.cleaned_data.get("consumer_secret", "")
        }
        with open(WC_CONFIG_FILE, "w") as file:
            json.dump(config, file)
