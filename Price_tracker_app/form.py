from django import forms
from .models import Feedback

class login_form(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = '__all__'