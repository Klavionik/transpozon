from django import forms
from django.contrib.auth.forms import UserCreationForm

from shop.models import User, Feedback


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = '__all__'
        widgets = {
            'text': forms.Textarea,
            'rating': forms.RadioSelect,
            'product': forms.HiddenInput,
        }
