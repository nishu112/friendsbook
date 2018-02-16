from django.forms import ModelForm
from django.contrib.auth.models import User
from friendsbook.models import *
from betterforms.multiform import MultiModelForm
from django.forms import widgets
from django.utils import six
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError





class SignUpForm(ModelForm):
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
	class Meta:
		model=User
		fields = ["username","password"]

class Cover(ModelForm):
	class Meta:
		model=Status
		fields=["image"]
