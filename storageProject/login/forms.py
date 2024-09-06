from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm

class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Username or Email')

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email and password:
            user = authenticate(username=username_or_email, password=password)
            if user is None:
                # Try to authenticate with email
                try:
                    user_model = get_user_model()
                    user_instance = user_model.objects.get(email=username_or_email)
                    user = authenticate(username=user_instance.username, password=password)
                except user_model.DoesNotExist:
                    user = None

            if user is None:
                raise forms.ValidationError('Invalid login credentials')
            self.cleaned_data['user'] = user

        return self.cleaned_data
