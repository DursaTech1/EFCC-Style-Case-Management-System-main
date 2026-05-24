from django import forms
from .models import Case, Evidence, User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# forms.py

class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['title', 'description', 'status', 'assigned_to']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow investigators or lawyers to be assigned
        self.fields['assigned_to'].queryset = User.objects.filter(role__in=['lawyer', 'investigator'])


class EvidenceForm(forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ['file', 'description']




class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
