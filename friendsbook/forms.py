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
	password = forms.CharField(
		widget=forms.PasswordInput(attrs={'class':'form-control'}),
		max_length=35,
		required=True)
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

class CreateGroup(ModelForm):
	OPEN = 'OP'
	CLOSED = 'CL'
	PRIVACY_CHOICES = (
		(OPEN, 'OPEN'),
		(CLOSED, 'CLOSED'),
	)
	gname=forms.CharField(
		widget=forms.TextInput(attrs={'class':'form-control'}),
		max_length=35,
		required=True)
	privacy=forms.ChoiceField(widget = forms.Select(attrs={'class':'form-control'}),
                     choices=PRIVACY_CHOICES, initial='CL', required = True)

	class Meta:
		model=Groups
		fields=["gname","privacy"]

class LoginForm(ModelForm):

	username = forms.CharField(
		widget=forms.TextInput(attrs={'class':'form-control'}),
		max_length=35,
		required=True,
		error_messages={'required': 'Please enter your name hethg'})

	password = forms.CharField(
		widget=forms.PasswordInput(attrs={'class':'form-control'}),
		max_length=35,
		required=True,
		error_messages={'required': 'Wrong password'})

	class Meta:
		model=User
		fields = ["username","password"]

	def clean(self):
		cleaned_data = super(LoginForm, self).clean()
		username = cleaned_data.get('username')
		password = cleaned_data.get('password')
		print(username)
		print(password)
		print('hey')
		if not username:
			raise forms.ValidationError('You have to write something!')

class Cover(ModelForm):
	class Meta:
		model=Status
		fields=["image"]
