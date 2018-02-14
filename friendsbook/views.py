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
from .models import *
from .forms import *
from .import views
import json
from django.contrib.auth.forms import UserCreationForm

from django.http import JsonResponse
from django.db.models import Q
from django.core import serializers
from django.core.serializers import serialize
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.template.loader import render_to_string


def user_post(request,user):
	posts=Status.objects.all().select_related('username').order_by('-time')
	# modify it to get all the timeline posts
	for x in posts:
		x.likes=StatusLikes.objects.filter(sid=x).count()
		x.comments=Comment.objects.filter(sid=x).count()
		x.is_like=StatusLikes.objects.filter(username=request.user,sid=x).count()
	return posts

def Check_user_online(request):
	chatusers=User.objects.select_related('logged_in_user')
	for user in chatusers:
		user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
	return chatusers

def group_list(request):
	groups=Groups.objects.all()
	return groups

class GroupsView(generic.DetailView):
	model = Groups

	def get_queryset(self):
		user=self.request.user.username
		user=Groups.objects.get(username=user)
		return Groups.objects.all().select_related('username').order_by('-time')

	def get_context_data(self, **kwargs):
		context = super(GroupView,self).get_context_data(**kwargs)
		return context


def user_list_data(request):
	users = User.objects.select_related('logged_in_user')
	for user in users:
		user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
	return users

def user_list(request):
	users=user_list_data(request)

	return render(request, 'chat/main_chat.html', {'chatusers': users})
	#remove these lines

#get all the friends
def FriendList(request,user):
	friends=Profile.objects.all()
	return friends


##searching of user

def friends_list(request,searched_by,context):
	addfriends_list=list()

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


def home(request):
	posts=user_post(request,request.user)
	chatusers=Check_user_online(request)
	groups=group_list(request)
	return render(request,"home/index.html",{'posts':posts,'chatusers':chatusers,'groups':groups})

def grouphome(request):
	return render(request,"groups/index.html")






class UploadProfile(View):
	def get(self, request):
		user=self.request.username
		ProfileObj=Profile.objects.get(username=User.objects.get(username=user))
		return render(self.request,'user/profile.html', {'ProfileObj':ProfileObj})

	def post(self, request):
		form = UpdateProfile(self.request.POST, self.request.FILES)
		if form.is_valid():
			ProfileForm=form.save(commit=False)
			ProfileForm.username=User.objects.get(username=self.request.user.username)
			ProfileForm.title="Updated Profile"
			ProfileForm.privacy='fs'
			ProfileForm.save()
			Profile.objects.filter(username=self.request.user).update(sid=Status.objects.get(id=ProfileForm.id))
			obj=Status.objects.get(id=ProfileForm.id)
			data = {'is_valid': True,'url':obj.image.url}
		else:
			data = {'is_valid': False}
		return JsonResponse(data)


class UploadCover(View):
	def get(self, request):
		user=self.request.username
		CoverObj=Profile.objects.get(username=User.objects.get(username=user))
		return render(self.request,'user/profile.html', {'CoverObj':CoverObj})

	def post(self, request):
		form = UpdateCover(self.request.POST, self.request.FILES)
		if form.is_valid():
			CoverForm=form.save(commit=False)
			CoverForm.username=User.objects.get(username=self.request.user.username)
			CoverForm.title="Updated Cover"
			CoverForm.privacy='fs'
			CoverForm.save()
			Profile.objects.filter(username=self.request.user).update(profileCover=Status.objects.get(id=CoverForm.id))
			obj=Status.objects.get(id=CoverForm.id)
			data = {'is_valid': True,'url':obj.image.url}
		else:
			data = {'is_valid': False}
		return JsonResponse(data)

def NewGroup(request):
	if request.is_ajax():
		gname=request.GET.get('gname',None)
		privacy=request.GET.get('privacy',None)
		Groups.objects.create(
		gname=gname,
		privacy=privacy
		)
		data = {'is_valid': True,'gname':gname}
		return JsonResponse(data)

#Comment this
def index(request):
	if request.user.is_authenticated:
		return render(request,"friendsbook/Home.html")
	return redirect(views.logout)  #update this functionality

def query(request):
	id=17
	username='nishu'
	query_set=likes=Status.objects.filter(id=12)
	query_set=User.objects.all()
	template_name='friendsbook/home.html'
	form=SubscribeForm(None)
	return render(request,template_name,{'data':query_set,'form':form})

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
		context=friends_list(self.request,self.request.user.username,context)
		return context

##this is for profile
class  FriendView(generic.DetailView):
	model=Profile
	context_object_name='User'
	template_name='user/profile.html'

	def get_context_data(self,**kwargs):
		context=super(FriendView,self).get_context_data(**kwargs)
		context['posts']=user_post(self.request,context['User'].username)
		searched_by=self.request.user.username
		# modify it to show send friend request
		context['chatusers']=Check_user_online(self.request)
		return context

def Timeline_friend_list(request):
	template_name="user/partial/friends_list.html"
	print('hello')
	if request.method == 'GET':
		str=request.GET.get('pathurl')
		currentusersearch=str.split("/")
		currentusersearch=(currentusersearch[3].split("-")[0])
		user=User.objects.get(username=currentusersearch)
		#Write query for friends list for a particular user
		friends_list=FriendList(request,user)
		friends_list = render_to_string(template_name, {'friends_list': friends_list})
	return JsonResponse(friends_list,safe=False)

def Timeline_photo_frame(request):
	template_name="user/partial/photo_frame.html"
	if request.method == 'GET':
		str=request.GET.get('pathurl')
		currentusersearch=str.split("/")
		currentusersearch=(currentusersearch[3].split("-")[0])
		user=User.objects.get(username=currentusersearch)
		photo_albums = Status.objects.filter(username=user)
		photo_albums = render_to_string(template_name, {'photo_albums': photo_albums})
		return JsonResponse(photo_albums,safe=False)

def Timeline_posts(request):
	template_name="user/partial/only_post.html"
	print('done')
	if request.method=='GET':
		str=request.GET.get('pathurl')
		currentusersearch=str.split("/")
		currentusersearch=(currentusersearch[3].split("-")[0])
		user=User.objects.get(username=currentusersearch)
		posts=user_post(request,user)
		status= render_to_string(template_name, {'posts': posts})
		return JsonResponse(status,safe=False)



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
		id=request.POST['id']
		type=request.POST['type']
		print(id)
		print(type)
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
			return HttpResponse(likes)
		if type=="Comment_like":
			print('not done')
			check=CommentLikes.objects.filter(username=User.objects.get(username=username)).filter(cid=Comment.objects.get(id=id))
			print('1 done')
			likes=Comment.objects.get(id=id).likes
			print('calculated')
			if not check.exists():
				#print("inside")
				likes=likes+1
				Comment.objects.filter(id=id).update(likes=likes)
				like=CommentLikes(username=User.objects.get(username=username),cid=Comment.objects.get(id=id))
				like.save()
			else:
				likes=likes-1
				Comment.objects.filter(id=id).update(likes=likes)
				CommentLikes.objects.filter(username=User.objects.get(username=username),cid=Comment.objects.get(id=id)).delete()
			print(likes)
			print('check')
			return HttpResponse(likes)

#ajax
def deleteCommentPost(request):
	if request.is_ajax():
		id=request.POST['id']
		type=request.POST['type']
		print(id)
		print('trying')
		print(type)
		if type=='delete_comment':
			Comment.objects.get(id=id).delete()
			print('Comment deleted')
		if type=='delete_status':
			Status.objects.get(id=id).delete()
			print('status deleted')
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
	if request.is_ajax():
		fuser=request.GET.get('fuser',None)
		type=request.GET.get('type',None)
		user=request.user.username
		user_obj=User.objects.get(username=user)
		fuser_obj=User.objects.get(username=fuser)
		##check again these conditions to make it more secure and reliable
		#not completed
		if type=='0':
			FriendsWith.objects.create(username=user_obj,fusername=fuser_obj)
		elif type=='1' or type=='3':
			#write code to update te result
			abc=FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj))
			FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj)).delete()
		elif type=='2':
			FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj)).update(confirm_request=2)
			abc=FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj))
		result=1
		return JsonResponse(result,safe=False)


def Comments(request):
	if request.is_ajax():
		if request.method=="POST":
			user=request.user
			sid=request.POST['Status']
			text=request.POST['post']
			sid=Status.objects.get(id=sid)
			comment=Comment.objects.create(username=user,text=text,sid=sid)
			noOflikesonComment=CommentLikes.objects.filter(cid=comment.id)
			likes=noOflikesonComment.count()
			jsonobj=render_to_string('uposts/partials/comment.html', {'comment': comment,'likes':likes},request)
			return JsonResponse(jsonobj,safe=False)
		else:
			sid=request.GET.get('sid',None)
			comments=Comment.objects.filter(sid=Status.objects.get(id=sid)).select_related('username')
			for x in comments:
				x.likes=CommentLikes.objects.filter(cid=x.id).count()
				x.is_like=CommentLikes.objects.filter(cid=x.id,username=request.user).count()

			jsonobj=render_to_string('uposts/partials/comments.html', {'comments': comments},request)
			return JsonResponse(jsonobj,safe=False)
			#below methods are not working? because of some unknown issues
			return render(request, 'uposts/partials/comments.html',{'comments': comments})

class PartialGroupView(TemplateView):
	def get_context_data(self, **kwargs):
		context = super(PartialGroupView, self).get_context_data(**kwargs)
	# update the context
		return context
