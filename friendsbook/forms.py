from django.forms import ModelForm
from django.contrib.auth.models import User
from friendsbook.models import *
from betterforms.multiform import MultiModelForm
from django import forms

class SignUpForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model=User
        fields = ["username","password","password"]

class ProfileForm(ModelForm):
    class Meta:
        model=Profile
        fields= ["fname","lname","emailid","gender"]


class CreatePost(ModelForm):
    class Meta:
        model=Status
        fields = ["text","image","privacy"]

class LoginForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model=User
        fields = ["username","password"]
