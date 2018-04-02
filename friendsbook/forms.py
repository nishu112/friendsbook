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
from django.core.exceptions import ObjectDoesNotExist

class advanceSearchForm(forms.Form):
	name=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Name'}),label='Name',
		max_length=30,required=False)
	InstituteName=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Institute Name'}),label='Institute',
		max_length=30,required=False)
	courseName=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Course/Class Name'}),label='Course/Class',
		max_length=30,required=False)
	Organisation=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Organisation Name'}),label='Organisation/Working',
		max_length=30,required=False)
	profile=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Job Profile'}),label='Job Profile',
		max_length=30,required=False)
	location=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Job Location'}),label='Location',
		max_length=30,required=False)

	def clean(self):
		super(advanceSearchForm, self).clean()
		name=self.cleaned_data.get('name')
		InstituteName=self.cleaned_data.get('InstituteName')
		courseName=self.cleaned_data.get('courseName')
		Organisation=self.cleaned_data.get('Organisation')
		profile=self.cleaned_data.get('profile')
		location=self.cleaned_data.get('location')
		print('inside form clean')
		print(InstituteName)
		if name=="" and InstituteName=="" and courseName=="" and Organisation=="" and profile==""  and location=="":
			print('hey')
			raise forms.ValidationError("Don't submit empty")
		if not name and not InstituteName and not courseName and not Organisation and not profile  and not location:
			raise forms.ValidationError("something went wrong")
		return self.cleaned_data



class EducationDetails(ModelForm):
	CHOICES = [(i,i) for i in range(1950,2019)]
	date=forms.ChoiceField(widget =forms.Select(),choices=CHOICES, label="Year",initial='2018', required = True)
	class Meta:
		model=Education
		exclude=["username"]

class WorkingFor(ModelForm):
	CHOICES = [(i,i) for i in range(1950,2019)]
	WorkingFrom=forms.ChoiceField(widget =forms.Select(),choices=CHOICES, label="Year",initial='2018', required = True)
	organisation=forms.CharField(required=False)
	class Meta:
		model=Working
		exclude=["username"]


class SignUpForm(ModelForm):
	MIN_LENGTH = 8
	username=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':"Enter Unique Username"}),help_text='Required. Minimum 5 characters . Letters, digits and @/./+/-/_ only.',label="Username",required=True)
	password = forms.CharField(
		widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':"Enter Password"}),
		max_length=35,
		required=True)
	confirm_password = forms.CharField(
		widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':"Re-enter Password"}),
		max_length=35,
		required=True)

	class Meta:
		model=User
		fields = ["username","password","confirm_password"]

	def clean(self):
		super(SignUpForm, self).clean()
		username= self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		if len(username) < 5:
			self._errors['username'] = self.error_class([
				'Minimum 5 characters required'])
		if len(password) < self.MIN_LENGTH:
			self._errors['password'] = self.error_class([
				'Minimum 8 characters required'])
		confirm_password = self.cleaned_data.get('confirm_password')
		id = self.cleaned_data.get('id')
		username= self.cleaned_data.get('username')
		if password != confirm_password:
			self._errors['confirm_password'] = self.error_class([
				'Passwords doesn\'t match'])
		return self.cleaned_data



class ProfileForm(ModelForm):
	Male = 'M'
	FeMale = 'F'
	GENDER_CHOICES = (
		(Male, 'Male'),
		(FeMale, 'Female'),
	)
	gender=forms.ChoiceField(widget =forms.RadioSelect(),choices=GENDER_CHOICES, initial='M', required = True)
	fname=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter First Name'}),label="First Name",required = True)
	lname=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter Last Name'}),label="Last Name",required=False)
	emailid = forms.EmailField(
	widget=forms.EmailInput(attrs={'class': 'form-control','placeholder':'Enter Your email'}),
	label="Email",required=True,
	)
	dob=forms.DateField(widget=forms.TextInput(attrs=
                                {
                                    'class':'datepicker form-control',
									'placeholder':'Enter your date of birth'
                                }),label="Date of Birth",
								required = True)
	class Meta:
		model=Profile
		fields= ["fname","lname","dob","emailid","gender"]

	def clean(self):
		super(ProfileForm, self).clean()
		email=self.cleaned_data.get('emailid')
		fname=self.cleaned_data.get('fname')
		lname=self.cleaned_data.get('lname')
		if not fname.isalpha():
			self._errors['fname'] = self.error_class([
				'Only alphabets allowed'])
		if not lname.isalpha():
			self._errors['lname'] = self.error_class([
				'Only alphabets allowed'])
		print(email)
		if  len(fname)<4:
			self._errors['fname'] = self.error_class([
				'Minimum 4 characters required'])
		if len(lname)<4:
			self._errors['lname'] = self.error_class([
				'Minimum 4 characters required'])
		print(email)
		return self.cleaned_data


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
	MIN_LENGTH=8
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
		password = self.cleaned_data.get('confirm_password')
		print(new_password)
		print(password)
		if len(password) < self.MIN_LENGTH:
			self._errors['new_password'] = self.error_class([
				'Minimum 8 characters required'])
		confirm_password = self.cleaned_data.get('confirm_password')
		id = self.cleaned_data.get('id')
		user = User.objects.get(pk=id)
		if not user.check_password(old_password):
			self._errors['old_password'] = self.error_class([
				'Old password don\'t match'])
		if password and new_password != confirm_password:
			self._errors['confirm_password'] = self.error_class([
				'Passwords don\'t match'])
		return self.cleaned_data


class EditProfileForm(ModelForm):
	fname=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter First Name'}),label="First Name",required = True)
	lname=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter Last Name'}),label="Last Name",required=False)
	emailid = forms.EmailField(
	widget=forms.EmailInput(attrs={'class': 'form-control','placeholder':'Enter Your email'}),
	label="Email",required=True,
	)


	dob=forms.DateField(widget=forms.TextInput(attrs=
                                {
                                    'class':'datepicker form-control',
                                }),label="Date of Birth",
								required = True)

	phone_no = forms.RegexField(regex=r'^\+?1?\d{9,15}$',widget=forms.TextInput(attrs={'class':'form-control'}))


	city = forms.CharField(
		widget=forms.TextInput(attrs={'class':'form-control'}),
		max_length=30,required=False)

	state = forms.CharField(
		widget=forms.TextInput(attrs={'class':'form-control'}),
		max_length=30,required=False)

	class Meta:
		model=Profile
		fields= ["fname","lname","emailid","dob","phone_no","state","city"]

	def clean(self):
		super(EditProfileForm, self).clean()
		fname=self.cleaned_data.get('fname')
		lname=self.cleaned_data.get('lname')
		phone=self.cleaned_data.get('phone_no')
		if not fname.isalpha():
			self._errors['fname'] = self.error_class([
				'Only alphabets allowed'])
		if not lname.isalpha():
			self._errors['lname'] = self.error_class([
				'Only alphabets allowed'])
		#print(email)
		if  len(fname)<4:
			self._errors['fname'] = self.error_class([
				'Minimum 4 characters required'])
		if len(lname)<5:
			self._errors['lname'] = self.error_class([
				'Minimum 4 characters required'])
		#print(email)
		if not phone:
			self._errors['phone_no']=self.error_class([
			'Wrong format of phone number'])
		return self.cleaned_data

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
		max_length=35,label='Group Name',
		required=True)
	privacy=forms.ChoiceField(widget = forms.Select(attrs={'class':'form-control'}),
                     choices=PRIVACY_CHOICES, initial='CL', required = True)

	class Meta:
		model=Groups
		fields=["gname","privacy"]

	def clean(self):
		cleaned_data = super(CreateGroup, self).clean()
		gname = cleaned_data.get('gname')
		privacy = cleaned_data.get('privacy')
		if len(gname)<4:
			self._errors['gname'] = self.error_class([
			'Group Name Should be at least 5 characters'])
		return self.cleaned_data

class LoginForm(ModelForm):

	username = forms.CharField(
		widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter username'}),
		max_length=35,
		required=True,
		error_messages={'required': 'Please enter your username '})

	password = forms.CharField(
		widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'provide password assosiated with username' }),
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
		flag=0
		try:
			flag=1
			user=User.objects.get(username=username)
			self._errors['username'] = self.error_class([''])
		except ObjectDoesNotExist:
			flag=0
			self._errors['username'] = self.error_class(['username doesn\'t exists'])
		if flag:
			self._errors['password'] = self.error_class([
			'Username and Passwords don\'t match'])
		return self.cleaned_data

class Cover(ModelForm):
	class Meta:
		model=Status
		fields=["image"]
