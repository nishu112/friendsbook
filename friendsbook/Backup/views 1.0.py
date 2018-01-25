from django.contrib.auth import authenticate,login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.utils.decorators import method_decorator
from django.shortcuts import HttpResponse,render,redirect
from django.core.files.storage import FileSystemStorage
from django.template.response import TemplateResponse
from django.views.generic.edit import CreateView
from django.views.generic import View
from django.views import generic
from .models import Status,Profile,Profile
from .forms import CreatePost,SignUpForm,LoginForm
from .import views

from django.contrib.auth import authenticate,login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.utils.decorators import method_decorator
from django.shortcuts import HttpResponse,render,redirect
from django.core.files.storage import FileSystemStorage
from django.template.response import TemplateResponse
from django.views.generic.edit import CreateView
from django.views.generic import View
from django.views import generic
from .models import Status,Profile
from .forms import CreatePost,SignUpForm,ProfileForm,LoginForm
from .import views

class RegistrationView(View):
	SignUp_class=SignUpForm
	Profile_class=ProfileForm
	template_name="user/SignUp.html"
	#get get request from form
	def get(self,request):
		user_form=self.SignUp_class(instance=self.request.user)
		profile_form=self.Profile_class(instance=self.request.user.profile)
		return render(request,self.template_name,{
	'user_form':user_form,
	'profile_form' :profile_form
	})
	##if we get post request from form
	def post(self,request):
		form=self.form_class(request.POST)
		if form.is_valid():
			user=form.save(commit=False)
			username = form.cleaned_data['username']
			raw_password = form.cleaned_data['password']
			user.set_password(raw_password)
			user.save()
			user=authenticate(username=username,password=raw_password)
			if user is not None:
				if user.is_active:
					auth_login(request,user)
					return redirect(views.index)
		return render(request,self.template_name,{'form':form})

class LoginView(View):
	form_class=LoginForm
	template_name="user/login.html"
	#get method
	def get(self,request):
		if request.user.is_authenticated:
			return redirect(views.index)
		form=LoginForm(None)
		return render(request,self.template_name,{'form':form})
	#post method
	def post(self,request):
		form=LoginForm(request.POST)
		username = request.POST['username']
		password = request.POST['password']
		user=authenticate(username=username,password=password)
		if user is not None:
			auth_login(request,user)
			return redirect(views.index)
		else:
			return render(request,"user/login.html",{'form':form})

def logout(request):
	auth.logout(request)
	return render(request,"user/logout.html")

class PostView(generic.ListView):
	template_name='uposts/home.html'
	context_object_name='status_object'

	def get_queryset(self):
		#print(self.request.user.username)
		name=self.request.user.username
		#return Status.objects.filter(username=self.request.user.username).order_by('-time')
		return Status.objects.all()
	#def get_queryset(request):
	#	return Status.objects.all().order_by('-time')

class PostDetailView(generic.DetailView):
	model=Status
	context_object_name='user_profile'
	template_name='uposts/detail.html'


def index(request):
	if request.user.is_authenticated:
		return render(request,"friendsbook/Home.html")
	return redirect(views.logout)  #update this functionality


def create_post(request):
	if request.method=="POST":
		form=CreatePost(request.POST,request.FILES)
		if form.is_valid():
			post=form.save(commit=False)
			print(request.user.username + " " + "not working")
			#name=request.user.username
			#query=Profile.objects.get(username=request.user.username)
			#post.username=query.username
			form.save()
			return redirect(views.index)
	else:
		form=CreatePost()
	return render(request,"uposts/createpost.html",{'form':form})


class FriendsView(generic.ListView):  ##print friendlist of user here
	template_name='user/all_profile.html'
	context_object_name='data'
	def get_queryset(self):
		return Profile.objects.all()

class  FriendView(generic.DetailView):
	model=Profile
	context_object_name='User'
	template_name='user/profile.html'


class LoginView(View):
	form_class=SignUpForm
	template_name="user/login.html"
	#get method
	def get(self,request):
		if request.user.is_authenticated:
			return redirect(views.index)
		form=LoginForm(None)
		return render(request,self.template_name,{'form':form})
	#post method
	def post(self,request):
		form=LoginForm(request.POST)
		username = request.POST['username']
		password = request.POST['password']
		user=authenticate(username=username,password=password)
		if user is not None:
			auth_login(request,user)
			return redirect(views.index)
		else:
			return render(request,"user/login.html",{'form':form})

def logout(request):
	auth.logout(request)
	return render(request,"user/logout.html")

class PostView(generic.ListView):
	template_name='uposts/home.html'
	context_object_name='status_object'

	def get_queryset(self):
		#print(self.request.user.username)
		name=self.request.user.username
		return Status.objects.filter(username=self.request.user.username).order_by('-time')
	#def get_queryset(request):
	#	return Status.objects.all().order_by('-time')

class PostDetailView(generic.DetailView):
	model=Status
	context_object_name='user_profile'
	template_name='uposts/detail.html'


def index(request):
	if request.user.is_authenticated:
		return render(request,"friendsbook/Home.html")
	return redirect(views.logout)  #update this functionality


def create_post(request):
	if request.method=="POST":
		form=CreatePost(request.POST,request.FILES)
		if form.is_valid():
			post=form.save(commit=False)
			print(request.user.username + " " + "not working")
			name=request.user.username
			query=Profile.objects.get(username=request.user.username)
			post.username=query.username
			form.save()
			return redirect(views.index)
	else:
		form=CreatePost()
	return render(request,"uposts/createpost.html",{'form':form})


class FriendsView(generic.ListView):  ##print friendlist of user here
	template_name='user/all_profile.html'
	context_object_name='data'
	def get_queryset(self):
		return Profile.objects.all()

class  FriendView(generic.DetailView):
	model=Profile
	context_object_name='User'
	template_name='user/profile.html'
