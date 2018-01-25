from django.contrib.auth import authenticate,login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.utils.decorators import method_decorator
from django.shortcuts import HttpResponse,render,redirect
from django.core.files.storage import FileSystemStorage
from django.template.response import TemplateResponse
from django.views.generic.edit import CreateView
from django.views.generic import View
from django.views import generic
from .models import Status,Profile,StatusLikes,FriendsWith,Message,Comment,Groups,CommentLikes
from .forms import CreatePost,SignUpForm,ProfileForm,LoginForm
from .import views
import json
from django.contrib.auth.forms import UserCreationForm
from django_ajax.decorators import ajax
from django.http import JsonResponse
from django.db.models import Q
from django.core import serializers

def user_list_data(request):
	users = User.objects.select_related('logged_in_user')
	for user in users:
		user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
	return users

def user_list(request):
	users=user_list_data(request)

	return render(request, 'chat/chat_list.html', {'users': users})
	#remove these lines
	users = Profile.objects.select_related('username')
	return render(request, 'chat/chat_list.html', {'users': users})


class RegistrationView(View):
	user_class=SignUpForm
	profile_class=ProfileForm
	template_name="user/signup.html"
	#get get request from form
	def get(self,request):
		user_form=self.user_class(None)
		profile_form=self.profile_class(None)
		return render(request,self.template_name,{'user_form':user_form ,'profile_form':profile_form})
	##if we get post request from 'form'
	def post(self,request):
		user_form=self.user_class(request.POST)
		profile_form=self.profile_class(request.POST)
		if ( user_form.is_valid() and profile_form.is_valid ):
			user=user_form.save(commit=False)
			username = user_form.cleaned_data['username']
			raw_password = user_form.cleaned_data['password']
			fname=request.POST['fname']
			lname=request.POST['lname']
			emailid=request.POST['emailid']
			gender=request.POST['gender']
			user.set_password(raw_password)
			user.save()
			id=User.objects.get(username=username).id
			Profile.objects.filter(username_id=id).update(fname=fname,lname=lname,emailid=emailid,gender=gender)
			return redirect('login')
			#user=authenticate(username=username,password=raw_password)
			#if user is not None:
#				if user.is_active:
#					auth_login(request,user)
					#return redirect('index')
				#verify though emailid first then login
				#create view for this
		return render(request,self.template_name,{'user_form':user_form,'profile_form':profile_form})

class LoginView(View):
	form_class=LoginForm
	template_name="user/login.html"
	#get method
	def get(self,request):
		if request.user.is_authenticated:
			return redirect('index')
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
			return redirect('index')
		else:
			return render(request,"user/login.html",{'form':form})

def logout(request):
	auth.logout(request)
	return render(request,"user/logout.html")

#update_profile   //Complete it using class based views
#@login_required
#@transaction.atomic
#def update_profile(request):
#    if request.method == 'POST':
#        user_form = UserForm(request.POST, instance=request.user)
#        profile_form = ProfileForm(request.POST, instance=request.user.profile)
#        if user_form.is_valid() and profile_form.is_valid():
#            user_form.save()
#            profile_form.save()
#            messages.success(request, _('Your profile was successfully updated!'))
#            return redirect('settings:profile')
#        else:
#            messages.error(request, _('Please correct the error below.'))
#    else:
#        user_form = UserForm(instance=request.user)
#        profile_form = ProfileForm(instance=request.user.profile)
#    return render(request, 'profiles/profile.html', {
#        'user_form': user_form,
#        'profile_form': profile_form
#    })

def group_list(request):
	groups=Groups.objects.all()
	return groups

class PostView(generic.ListView):
	template_name='uposts/post_list.html'
	context_object_name='status_object'
#paginate_by = 10
#use pagination to limit the number of post a user can see
#update this view later
	def get_queryset(self):
	#print(self.request.user.username)
	#name=self.request.user.username
	#return Status.objects.filter(username=self.request.user.username).order_by('-time')
		return Status.objects.all().select_related('username').order_by('-time')

	def get_context_data(self,**kwargs):
		context=super(PostView,self).get_context_data(**kwargs)
		comment_list=list()
		numberOfComments=list()
		for x in context['status_object']:
			newcomment=Comment.objects.filter(sid=x.id)
			#print(Status.objects.filter(id=x.id))
			numberOfComments.append(newcomment.count())
			comment_list.append(newcomment)
		#print(comment_list)
		context['status_object']=zip(context['status_object'],comment_list,numberOfComments)
		chatusers=User.objects.select_related('logged_in_user')
		for user in chatusers:
			user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
		context['users']=chatusers
		context['groups']=group_list(self.request)
		return context

class PostDetailView(generic.DetailView):
	model=Status
	context_object_name='status'
	template_name='uposts/post_detail.html'

	def get_queryset(self):
		return Status.objects.all().select_related('username').order_by('-time')

	def get_context_data(self,**kwargs):
		context=super(PostDetailView,self).get_context_data(**kwargs)
		context['users']=user_list_data(self.request)
		context['groups']=group_list(self.request)
		return context

#Comment this
def index(request):
	if request.user.is_authenticated:
		return render(request,"friendsbook/Home.html")
	return redirect(views.logout)  #update this functionality

def query(request):
	id=17
	username='nishu'
	print(username + " : "+ " is something else")
	query_set=likes=Status.objects.filter(id=12)
	print(username + " : "+ " is something else")
	query_set=User.objects.all()
	template_name='friendsbook/home.html'
	return render(request,template_name,{'data':query_set})

def create_post(request):
	if request.method=="POST":
		form=CreatePost(request.POST,request.FILES)
		if form.is_valid():
			post=form.save(commit=False)
			post.username=User.objects.get(username=request.user.username)
			form.save()
			return redirect('index')
	else:
		form=CreatePost()
	return render(request,"uposts/post_create.html",{'form':form})

class FriendsView(generic.ListView):  ##print friendlist of user here
	template_name='user/search_user.html'
	context_object_name='data'

	def get_queryset(self):
		if self.request.method=="GET" :
			fname = self.request.GET.get('search_user')
			return Profile.objects.filter(Q(fname__istartswith=fname) | Q(lname__istartswith=fname)).select_related('username').select_related('sid')

	def get_context_data(self,**kwargs):
		context=super(FriendsView,self).get_context_data(**kwargs)
		addfriends_list=list()
		searched_by=self.request.user.username
		for x in context['data']:
			if str(x.username)==searched_by:
				addfriends_list.append(-1)
			else:
				user=searched_by
				fuser=x.username
				user_obj=User.objects.get(username=user)
				fuser_obj=User.objects.get(username=fuser)
				friendship=FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj))
				if friendship.exists():
					for y in friendship:
						if y.confirm_request==2:
							addfriends_list.append(3)
						else:
							checkConnectionDirection=FriendsWith.objects.filter(username=user_obj,fusername=fuser_obj)
							if checkConnectionDirection.exists():
								addfriends_list.append(1)
							else:
								addfriends_list.append(2)
				#define
				#0-send request
				#1-cancel request
				#2- confirm request sent by user
				#3 unfriends( means already friends)
				else:
					addfriends_list.append(0)
		context['data']=zip(context['data'],addfriends_list)
		return context

##this is for profile
class  FriendView(generic.DetailView):
	model=Profile
	context_object_name='User'
	template_name='user/profile.html'

	def get_context_data(self,**kwargs):
		context=super(FriendView,self).get_context_data(**kwargs)
		searched_by=self.request.user.username
		context['status_object']=Status.objects.filter(username=User.objects.get(username=context['User'].username))
		comment_list=list()
		numberOfComments=list()
		for x in context['status_object']:
			newcomment=Comment.objects.filter(sid=x.id)
			numberOfComments.append(newcomment.count())
			if newcomment.exists():
				print(newcomment)
			comment_list.append(newcomment)
		context['status_object']=zip(context['status_object'],comment_list,numberOfComments)
		chatusers=User.objects.select_related('logged_in_user')
		for user in chatusers:
			user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
		context['users']=chatusers
		return context

def liveSearch(request):
	if request.is_ajax():
		fname=request.GET.get('search',None)
		obj=Profile.objects.filter(Q(fname__istartswith=fname)).select_related('username').select_related('sid')
		data = serializers.serialize('json', obj,use_natural_foreign_keys=True)
		return JsonResponse(data,safe=False)

def validate_username(request):
	username = request.GET.get('username', None)
	data = {
		'is_taken': User.objects.filter(username__iexact=username).exists()
	}
	return JsonResponse(data)

#using ajax to like a post
def like(request):
	if request.is_ajax():
		username = request.user.username
		id=request.GET.get('id',None)
		type=request.GET.get('type',None)
		if type=="post_like":
			check=StatusLikes.objects.filter(username=User.objects.get(username=username)).filter(sid=Status.objects.get(id=id))
			likes=Status.objects.get(id=id).likes
			if not check.exists():
				#print("inside")
				likes=likes+1
				Status.objects.filter(id=id).update(likes=likes)
				like=StatusLikes(username=User.objects.get(username=username),sid=Status.objects.get(id=id))
				like.save()
			else:
				likes=likes-1
				Status.objects.filter(id=id).update(likes=likes)
				StatusLikes.objects.filter(username=User.objects.get(username=username),sid=Status.objects.get(id=id)).delete()
			return JsonResponse(likes,safe=False)
		if type=="comment_like":
			print(id)
			check=CommentLikes.objects.filter(username=User.objects.get(username=username)).filter(cid=Comment.objects.get(slug=id))
			likes=Comment.objects.get(slug=id).likes
			if not check.exists():
				#print("inside")
				likes=likes+1
				Comment.objects.filter(slug=id).update(likes=likes)
				like=CommentLikes(username=User.objects.get(username=username),cid=Comment.objects.get(slug=id))
				like.save()
			else:
				likes=likes-1
				Comment.objects.filter(slug=id).update(likes=likes)
				CommentLikes.objects.filter(username=User.objects.get(username=username),cid=Comment.objects.get(slug=id)).delete()
			return JsonResponse(likes,safe=False)

#ajax
def deleteCommentPost(request):
	if request.is_ajax():
		id=request.GET.get('id',None)
		type=request.GET.get('type',None)
		if type=='comment':
			Comment.objects.get(slug=id).delete()
		if type=='status':
			Status.objects.get(id=id).delete()
		response=1
		return JsonResponse(response,safe=False)
#ajax function
def user_messages(request):
	if request.is_ajax():
		user=request.user.username
		fuser=request.GET.get('fuser',None)
		user_obj=User.objects.get(username=user)
		fuser_obj=User.objects.get(username=fuser)
		msg_obj=Message.objects.filter(Q(username=user_obj,fusername=fuser_obj)
		|Q(username=fuser_obj,fusername=user_obj)).select_related('username')
		msg_list=list(msg_obj.values())
		#print(msg_list.username)
		data = serializers.serialize('json', msg_obj,use_natural_foreign_keys=True)
		return JsonResponse(data,safe=False)

#define
#0-send request
#1-cancel request
#2- confirm request sent by user
#3 unfriends( means already friends)

def AddFriend(request):
	print("incoming")
	if request.is_ajax():
		fuser=request.GET.get('fuser',None)
		type=request.GET.get('type',None)
		user=request.user.username
		print(user)
		print(fuser)
		print(type)
		user_obj=User.objects.get(username=user)
		print(type)
		fuser_obj=User.objects.get(username=fuser)
		print("mytype")
		print("in")
		##check again these conditions to make it more secure and reliable
		#not completed
		if type=='0':
			print("created relation")
			FriendsWith.objects.create(username=user_obj,fusername=fuser_obj)
		elif type=='1' or type=='3':
			print("deleted")
			#write code to update te result
			abc=FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj))
			FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj)).delete()
			if abc.exists():
				print("done13")
			else:
				print("not ok13")
		elif type=='2':
			print("updation in progress")
			print(user)
			print(fuser)
			FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj)).update(confirm_request=2)
			abc=FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj))
			if abc.exists():
				print("done2")
			else:
				print("not ok2")
		result=1
		print("ok")
		return JsonResponse(result,safe=False)

def AddComment(request):
	if request.is_ajax():
		username=request.user.username
		text=request.GET.get('text',None)
		sid=request.GET.get('sid',None)
		user_obj=User.objects.get(username=username)
		sid=Status.objects.get(id=sid)
		Comment.objects.create(username=user_obj,text=text,sid=sid)
		return JsonResponse(text,safe=False)
