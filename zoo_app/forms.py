from django import forms
from django.contrib.auth.models import User
from zoo_app.models import UserProfile, Task, Resource


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ()


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'deadline')
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('title', 'content', 'url', 'type')
