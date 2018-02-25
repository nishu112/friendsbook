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
from django.contrib.admin.widgets import AdminDateWidget



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

class EditAboutGroup(ModelForm):

	about=forms.CharField(
	widget=forms.Textarea(attrs={'class':'form-control','placeholder':"Write Something about Group "}),
	label="",required=True)

	class Meta:
		model=Groups
		fields=["about"]

class ChattingForm(ModelForm):
	fusername=forms.CharField(widget=forms.TextInput(attrs={'type':'hidden'}),label="",required=True)
	text=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),
	label="",required=True)
	class Meta:
		model=Message
		fields=["fusername","text"]





class ChangePasswordForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput())
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Old password",
        required=True)

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New password",
        required=True)
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm new password",
        required=True)

    class Meta:
        model = User
        fields = ['id', 'old_password', 'new_password', 'confirm_password']

    def clean(self):
        super(ChangePasswordForm, self).clean()
        old_password = self.cleaned_data.get('old_password')
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        id = self.cleaned_data.get('id')
        user = User.objects.get(pk=id)
        if not user.check_password(old_password):
            self._errors['old_password'] = self.error_class([
                'Old password don\'t match'])
        if new_password and new_password != confirm_password:
            self._errors['new_password'] = self.error_class([
                'Passwords don\'t match'])
        return self.cleaned_data


class EditProfileForm(ModelForm):

	fname = forms.CharField(
		widget=forms.TextInput(attrs={'class':'form-control'}),
		label="First Name",
		max_length=20)

	lname = forms.CharField(
		widget=forms.TextInput(attrs={'class':'form-control'}),
		label="Last Name",
		max_length=20)

	emailid = forms.EmailField(
	widget=forms.EmailInput(attrs={'class': 'form-control'}),
	label="Emailid",
	max_length=30,
	)


	dob=forms.DateField(widget=forms.TextInput(attrs=
                                {
                                    'class':'datepicker form-control',


                                }),label="Date of Birth",
								required = False)

	phone_no = forms.RegexField(regex=r'^\+?1?\d{9,15}$',widget=forms.TextInput(attrs={'class':'form-control'}))


	city = forms.CharField(
		widget=forms.TextInput(attrs={'class':'form-control'}),
		max_length=30,)

	state = forms.CharField(
		widget=forms.TextInput(attrs={'class':'form-control'}),
		max_length=30,)
	class Meta:
		model=Profile
		fields= ["fname","lname","emailid","dob","phone_no","city","state"]


class CreatePost(ModelForm):
	class Meta:
		model=Status
		fields = ["text","image","privacy"]
	def clean(self):
		cleaned_data = super(CreatePost, self).clean()
		text = cleaned_data.get('text')
		image = cleaned_data.get('image')
		privacy = cleaned_data.get('privacy')
		if not text and not image and not privacy or not privacy or not text and not image:
			raise forms.ValidationError("Don't submit empty")


class CreateGroupPost(ModelForm):
	class Meta:
		model=Status
		fields = ["text","image"]

	def clean(self):
		cleaned_data = super(CreateGroupPost, self).clean()
		text = cleaned_data.get('text')
		image = cleaned_data.get('image')
		if not text and not image:
			raise forms.ValidationError("Don't submit empty")


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

	def clean(self):
		cleaned_data = super(CreateGroupPost, self).clean()
		gname = cleaned_data.get('gname')
		privacy = cleaned_data.get('privacy')
		if not gname or not privacy:
			raise forms.ValidationError("Don't submit empty")

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
