from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Userprofile

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(max_length=255, required=True)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'input' 
        self.fields['first_name'].widget.attrs['class'] = 'input'  
        self.fields['last_name'].widget.attrs['class'] = 'input' 
        self.fields['email'].widget.attrs['class'] = 'input' 
        self.fields['password1'].widget.attrs['class'] = 'input' 
        self.fields['password2'].widget.attrs['class'] = 'input'
    

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("The email is already taken.")
        return email


class UserprofileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserprofileForm, self).__init__(*args, **kwargs)

        self.fields['contact_number'].widget.attrs['class'] = 'input'
        self.fields['address'].widget.attrs['class'] = 'input'
        self.fields['zip_code'].widget.attrs['class'] = 'input'

    class Meta:
        model = Userprofile
        fields = ['contact_number', 'address', 'zip_code']


class ProfileCompletionForm(forms.ModelForm): 
    username = forms.CharField(required=True)
    
    class Meta:
        model = Userprofile
        fields = ['contact_number', 'address', 'zip_code']
    
    def __init__(self, *args, **kwargs):
        super(ProfileCompletionForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'input'})
