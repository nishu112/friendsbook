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
from django.shortcuts import get_object_or_404
from django.template.context_processors import csrf
from django.contrib.auth import update_session_auth_hash

from django.http import JsonResponse
from django.db.models import Q
from django.core import serializers
from django.core.serializers import serialize
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist

def fishy(request):
	return HttpResponse('Something Fishy is going on')

def user_post(request,user,posts):
	# modify it to get all the timeline posts
	for x in posts:
		x.likes=StatusLikes.objects.filter(sid=x).count()
		x.comments=Comment.objects.filter(sid=x).count()
		x.is_like=StatusLikes.objects.filter(username=request.user,sid=x).count()
	return posts

def Check_user_online(request,user):
	obj1=FriendsWith.objects.filter(username=user,confirm_request=2,blocked_status=0).select_related('fusername').values('fusername')
	obj1=User.objects.filter(id__in=obj1)
	obj2=FriendsWith.objects.filter(fusername=user,confirm_request=2,blocked_status=0).select_related('username').values('username')
	obj2=User.objects.filter(id__in=obj2)
	obj=obj1 | obj2
	chatusers=obj
	for user in chatusers:
		user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
	return chatusers

def group_list(request):
	groups=ConsistOf.objects.filter(username=request.user,confirm=1).select_related('gid')
	return groups



def user_list_data(request):
	users = User.objects.select_related('logged_in_user')
	for user in users:
		user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
	return users

def user_list(request):
	users=Check_user_online(request,request.user)

	return render(request, 'chat/main_chat.html', {'chatusers': users})
	#remove these lines

def FriendsOfFriends(request,user):
	chatusers=Check_user_online(request,User.objects.get(username=user))
	friends_suggestion=User.objects.none()
	for x in chatusers:
		y=Check_user_online(request,x)
		friends_suggestion= friends_suggestion | y
	user=User.objects.filter(username=user)
	user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
	chatusers=user|chatusers
	friends_suggestion=friends_suggestion|chatusers
	return friends_suggestion

#get all the friends
def FriendList(request,user):
	friends=Profile.objects.all()
	return friends


##searching of user

def friendship(user_obj,fuser_obj):
	friendship=FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj))
	if friendship.exists():
		for y in friendship:
			if y.confirm_request==2:
				return 3
			else:
				checkConnectionDirection=FriendsWith.objects.filter(username=user_obj,fusername=fuser_obj)
				if checkConnectionDirection.exists():
					return 1
				else:
					return 2
	else:
		return 0


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
			addfriends_list.append(friendship(user_obj,fuser_obj))
	context['data']=zip(context['data'],addfriends_list)
	return context
	#define
	#0-send request
	#1-cancel request
	#2- confirm request sent by user
	#3 unfriends( means already friends)

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
			print(form.errors)
			print(form)


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



def GetUserPosts(request):
	chatusers=Check_user_online(request,request.user)
	friends_suggestion=FriendsOfFriends(request,request.user)
	user=User.objects.filter(username=request.user)
	user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
	friendsAndMe=chatusers|user


	friends_suggestion=User.objects.filter(id__in=friends_suggestion).exclude(id__in=friendsAndMe)
	friendsPostWithoutGroup=Status.objects.filter(username__in=chatusers,gid__isnull=True).exclude(privacy='Me').select_related('username').order_by('-time')##friends Posts
	tempfriendsPostWithGroupPrivacyOpen=Status.objects.filter(username__in=chatusers,gid__isnull=False).exclude(privacy='CL').select_related('username').order_by('-time')
	friendsPostWithGroupPrivacyOpen=Status.objects.none()
	UserPartOfGroup=ConsistOf.objects.filter(username=request.user).values('gid')
	PostOfUserPartOfGroup=Status.objects.filter(gid__in=UserPartOfGroup)
	for x in tempfriendsPostWithGroupPrivacyOpen:
		if x.gid.privacy=='OP':
			friendsPostWithGroupPrivacyOpen=friendsPostWithGroupPrivacyOpen|Status.objects.filter(id=x.id)
	myPosts=Status.objects.filter(username=request.user).select_related('username').order_by('-time')
	friendsOfFriendsPosts=Status.objects.filter(username__in=friends_suggestion,gid__isnull=True).exclude(privacy='Me').exclude(privacy='fs').select_related('username').order_by('-time')
	posts=friendsPostWithoutGroup|friendsPostWithGroupPrivacyOpen|myPosts|friendsOfFriendsPosts|PostOfUserPartOfGroup
	return posts



def home(request):
	chatusers=Check_user_online(request,request.user)
	user=User.objects.filter(username=request.user)
	user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
	friends_suggestion=FriendsOfFriends(request,request.user)
	friendsAndMe=chatusers|user
	friends_suggestion=User.objects.filter(id__in=friends_suggestion).exclude(id__in=friendsAndMe)
	posts=user_post(request,request.user,GetUserPosts(request))
	groups=group_list(request)
	return render(request,"home/index.html",{'posts':posts,'chatusers':chatusers,'groups':groups,'friends_suggestion':friends_suggestion,'newGroupForm':CreateGroup(None)})

def PostDetailView(request,slug):
	print('hii')
	status=Status.objects.get(slug=slug)
	chatusers=Check_user_online(request,request.user)
	user=User.objects.filter(username=request.user)
	user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
	friends_suggestion=FriendsOfFriends(request,request.user)
	friendsAndMe=chatusers|user
	friends_suggestion=User.objects.filter(id__in=friends_suggestion).exclude(id__in=friendsAndMe)
	status.likes=StatusLikes.objects.filter(sid=status).count()
	status.comments=Comment.objects.filter(sid=status).count()
	status.is_like=StatusLikes.objects.filter(username=request.user,sid=status).count()

	groups=group_list(request)
	template_name='uposts/single_post.html'
	return render(request,template_name,{'status':status,'chatusers':chatusers,'friends_suggestion':friends_suggestion,'groups':groups})

def AboutGroup(request,pk):
	group=get_object_or_404(Groups, id=pk)

	try:
	    result=ConsistOf.objects.get(username=request.user,gid=group)
	except ObjectDoesNotExist:
	    result = None
	if result and result.confirm==1:
		group.new=0
	else:
		group.new=1
	if result==None:
		group.relation=0
	else:
		group.relation=1

	if group.privacy=='CL' and result==None or result and result.confirm==0:
		return redirect('groupMembers',pk=pk)



	#check user have the permission to access this group
	#only then user able to access this method
	chatusers=Check_user_online(request,request.user)
	try:
	    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
	except ObjectDoesNotExist:
	    group_consist=None

	return render(request,"groups/partial/about.html",{'group':group,'chatusers':chatusers,'group_consist':group_consist})



def grouphome(request,pk):
	group=get_object_or_404(Groups, id=pk)

	try:
	    result=ConsistOf.objects.get(username=request.user,gid=group)
	except ObjectDoesNotExist:
	    result = None
	if result and result.confirm==1:
		group.new=0
	else:
		group.new=1
	if result==None:
		group.relation=0
	else:
		group.relation=1

	if group.privacy=='CL' and result==None or result and result.confirm==0:
		return redirect('groupMembers',pk=pk)

	if request.method=='POST':
		print('post form')
		form=CreateGroupPost(request.POST,request.FILES)
		if form.is_valid():
			print('Hii')
			post=form.save(commit=False)
			post.username=User.objects.get(username=request.user.username)
			post.title="posted in "
			post.gid=group

			post=form.save()
			Notification.objects.create(from_user=request.user,gid=group,notification_type='PG')
		return HttpResponseRedirect(request.path_info)
		print('byee')

	else:
		form =CreateGroupPost(None)
		#check user have the permission to access this group
		#only then user able to access this method
		posts=Status.objects.filter(gid=group).select_related('username').order_by('-time')
		posts=user_post(request,request.user,posts)
		chatusers=Check_user_online(request,request.user)
		try:
		    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
		except ObjectDoesNotExist:
		    group_consist=None

		return render(request,"groups/index.html",{'posts':posts,'group':group,'form':form,'chatusers':chatusers,'group_consist':group_consist})

def groupMembers(request,pk):
	group=get_object_or_404(Groups, id=pk)

	try:
	    result=ConsistOf.objects.get(username=request.user,gid=group)
	except ObjectDoesNotExist:
	    result = None
	if result and result.confirm==1:
		group.new=0
	else:
		group.new=1

	if result==None:
		group.relation=0
	else:
		group.relation=1



	#check user have the permission to access this group
	#only then user able to access this method
	chatusers=Check_user_online(request,request.user)
	print(chatusers)
	members=ConsistOf.objects.filter(gid=group,gadmin=0,confirm=1).select_related('username')
	admins=ConsistOf.objects.filter(gid=group,gadmin=1).select_related('username')
	try:
	    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
	except ObjectDoesNotExist:
	    group_consist=None

	print(group_consist)
	return render(request,"groups/partial/group_members.html",{'group_members':members,'group':group,'chatusers':chatusers,'admins':admins,'group_consist':group_consist,'group_consist':group_consist})



def GroupsPhotos(request,pk):
	group=get_object_or_404(Groups, id=pk)

	try:
	    result=ConsistOf.objects.get(username=request.user,gid=group)
	except ObjectDoesNotExist:
	    result = None
	if result and result.confirm==1:
		group.new=0
	else:
		group.new=1

	if result==None:
		group.relation=0
	else:
		group.relation=1

	if group.privacy=='CL' and result==None or result and result.confirm==0:
		return redirect('groupMembers',pk=pk)

	chatusers=Check_user_online(request,request.user)

	posts=Status.objects.filter(gid=group).select_related('username').order_by('-time')
	photo_albums=Status.objects.filter(gid=group)
	try:
	    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
	except ObjectDoesNotExist:
	    group_consist=None
	return render(request,"groups/partial/photo_frame.html",{'group':group,'chatusers':chatusers,'group_consist':group_consist,'photo_albums': photo_albums})
		#update this to just load the group photos

def Groupfiles(request,pk):
	group=get_object_or_404(Groups, id=pk)

	try:
	    result=ConsistOf.objects.get(username=request.user,gid=group)
	except ObjectDoesNotExist:
	    result = None
	if result and result.confirm==1:
		group.new=0
	else:
		group.new=1

	if result==None:
		group.relation=0
	else:
		group.relation=1

	if group.privacy=='CL' and result==None or result and result.confirm==0:
		return redirect('groupMembers',pk=pk)

	chatusers=Check_user_online(request,request.user)

	posts=Status.objects.filter(gid=group).select_related('username').order_by('-time')
	photo_albums=Status.objects.filter(gid=group)
	try:
	    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
	except ObjectDoesNotExist:
	    group_consist=None
	files=Status.objects.none()
	return render(request,"groups/partial/files.html",{'group':group,'chatusers':chatusers,'group_consist':group_consist,'files':files})

def GroupsSettings(request,pk):
	group=get_object_or_404(Groups, id=pk)
	print('Hii')

	try:
	    result=ConsistOf.objects.get(username=request.user,gid=group)
	except ObjectDoesNotExist:
	    result = None
	if result and result.confirm==1:
		group.new=0
	else:
		group.new=1

	if result==None:
		group.relation=0
	else:
		group.relation=1
	if group.privacy=='CL' and result==None or result and result.confirm==0 or group.new is 1:
		return redirect('groupMembers',pk=pk)



	#check user have the permission to access this group
	#only then user able to access this method
	chatusers=Check_user_online(request,request.user)
	print(chatusers)
	members=ConsistOf.objects.filter(gid=group,gadmin=0,confirm=1).select_related('username')
	admins=ConsistOf.objects.filter(gid=group,gadmin=1).select_related('username')
	try:
	    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
	except ObjectDoesNotExist:
	    group_consist=None


	if request.method=='POST':
		print('coming to settings cahnges')
		form=CreateGroup(request.POST,instance=group)
		print('coming to settings')
		if form.is_valid():
			print('dnoe')
			form.save()
		return redirect('AboutGroup',group.id)
	else:
		print('ok till here')
		form=CreateGroup(instance=group)
		return render(request,"groups/partial/settings.html",{'group':group,'chatusers':chatusers,'group_consist':group_consist,'form':form})


def EditAboutGroupInfo(request,pk):
	group=get_object_or_404(Groups, id=pk)
	print('Hii')

	try:
	    result=ConsistOf.objects.get(username=request.user,gid=group)
	except ObjectDoesNotExist:
	    result = None
	if result and result.confirm==1:
		group.new=0
	else:
		group.new=1

	if result==None:
		group.relation=0
	else:
		group.relation=1



	#check user have the permission to access this group
	#only then user able to access this method
	chatusers=Check_user_online(request,request.user)
	print(chatusers)
	members=ConsistOf.objects.filter(gid=group,gadmin=0,confirm=1).select_related('username')
	admins=ConsistOf.objects.filter(gid=group,gadmin=1).select_related('username')
	try:
	    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
	except ObjectDoesNotExist:
	    group_consist=None


	if request.method=='POST':
		print('coming to post')
		form=EditAboutGroup(request.POST,instance=group)
		print('coming to post')
		if form.is_valid():
			about=request.POST['about']
			Groups.objects.filter(id=pk).update(about=about)
		return redirect('AboutGroup',group.id)
	else:
		print('ok till here')
		form=EditAboutGroup(instance=group)
		return render(request,"groups/partial/Edit about.html",{'group':group,'chatusers':chatusers,'group_consist':group_consist,'form':form})


def LeaveGroup(request):
	if request.is_ajax() and request.method=='POST':
		gid=request.POST['id']
		group=get_object_or_404(Groups,id=gid)
		ConsistOf.objects.filter(username=request.user,gid=group).delete()
		noOfAdminLeft=len(ConsistOf.objects.filter(gid=group),admin=1)
		members=0
		if noOfAdminLeft is 0:
			members=len(ConsistOf.objects.filter(gid=group))
			if members is 0:
				return redirect('index')
			else:
				#user with highest number of post will be made admin
				groupMembers=ConsistOf.objects.filter(gid=group)
				newadmin=groupMembers[:1]
				Max=-1
				for x in groupMembers:
					x.noOfPosts=Status.objects.filter(username=x.username,gid=group)
					if max<x.noOfPosts:
						newadmin=x
						max=x.noOfPosts
				ConsistOf.objects.filter(gid=group,username=x.username).update(gadmin=1,confirm=1)
				ConsistOf.objects.all()


		return redirect('GroupsHomepage',pk=group.id)

def ManageGroupMember(request,pk):
	group=get_object_or_404(Groups, id=pk)

	try:
	    result=ConsistOf.objects.get(username=request.user,gid=group)
	except ObjectDoesNotExist:
	    result = None
	if result and result.confirm==1:
		group.new=0
	else:
		group.new=1

	if result==None:
		group.relation=0
	else:
		group.relation=1
	try:
	    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
	except ObjectDoesNotExist:
	    group_consist=None

	if group.privacy=='CL' and result==None or result and result.confirm==0 or group_consist.gadmin==0:
		return redirect('groupMembers',pk=pk)

	chatusers=Check_user_online(request,request.user)
	pendingrequests=ConsistOf.objects.filter(gid=group,confirm=0)
	print(pendingrequests)
	return render(request,"groups/partial/pending members.html",{'group':group,'chatusers':chatusers,'group_consist':group_consist,'pendingrequests':pendingrequests})
		#update this to just load the group photos


def groupVideos(request,pk):
	group=get_object_or_404(Groups, id=pk)

	try:
	    result=ConsistOf.objects.get(username=request.user,gid=group)
	except ObjectDoesNotExist:
	    result = None
	if result and result.confirm==1:
		group.new=0
	else:
		group.new=1
	if result==None:
		group.relation=0
	else:
		group.relation=1

	if group.privacy=='CL' and result==None or result and result.confirm==0:
		return redirect('groupMembers',pk=pk)

	form =CreateGroupPost(None)
	#check user have the permission to access this group
	#only then user able to access this method
	posts=Status.objects.filter(gid=group).select_related('username').order_by('-time')
	posts=user_post(request,request.user,posts)
	chatusers=Check_user_online(request,request.user)
	try:
	    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
	except ObjectDoesNotExist:
	    group_consist=None
	videos=Status.objects.none()
	return render(request,"groups/partial/videos.html",{'group':group,'chatusers':chatusers,'group_consist':group_consist})


def MemberListActions(request):
	if request.is_ajax() and request.method=='POST':
		action=request.POST['action']
		gid=request.POST['gid']
		username=request.POST['user']
		group=get_object_or_404(Groups,pk=gid)
		user=get_object_or_404(User,username=username)
		print('Hello')
		print(username)
		print('Here')

		if action=='Make him admin':
			ConsistOf.objects.filter(gid=group,username=user).update(gadmin=1,confirm=1)
		elif action=='Remove From group':
			ConsistOf.objects.filter(gid=group,username=user).delete()
		elif action=='Remove from admin':
			ConsistOf.objects.filter(gid=group,username=user).update(gadmin=0)
		else:
			return JsonResponse(0,safe=False)
		try:
			member=ConsistOf.objects.get(gid=group,username=user,confirm=1)
		except ObjectDoesNotExist:
			member=None
		group_consist=group
		group.new=0
		try:
		    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
		except ObjectDoesNotExist:
		    group_consist=None
		try:
		    user_isadmin=ConsistOf.objects.get(gid=group,username=user,confirm=1)
		except ObjectDoesNotExist:
		    user_isadmin=None
		if user_isadmin is None:
			return JsonResponse(0,safe=False)
		content=render_to_string('groups/partial/custom_button_for_members.html', {'group_consist':group_consist,'group':group,'member':member,'user_isadmin':user_isadmin},request)
		print(content)
		return JsonResponse(content,safe=False)

def UploadGroupCover(request):
	if request.is_ajax and request.method=='POST':
		print("insife")
		form=Cover(request.POST,request.FILES)
		print(request.POST)
		gid=request.POST['gid']
		group=get_object_or_404(Groups,id=gid)
		if form.is_valid():
			cover=form.save(commit=False)
			cover.username=request.user
			cover.title="Posted in "
			cover.gid=group
			##correct this behavior right now only changing cover for a specific group
			cover.save()
			Notification.objects.create(from_user=request.user,gid=group,notification_type='PG')
			sid=Status.objects.get(id=cover.id)
			Groups.objects.filter(id=gid).update(cover=sid)
			gid=Groups.objects.get(id=gid)
			obj=Status.objects.get(id=cover.id)
			data = {'is_valid': True,'url':obj.image.url}
		else:
			data = {'is_valid': False}
		print("ok")
		return JsonResponse(data,safe=False)

def joinrequest(request):
	if request.is_ajax and request.method=='POST':
		gid=request.POST['id']
		data=request.POST['data']
		print(gid)
		print(data)
		group=get_object_or_404(Groups,id=gid)
		if data=='Request To join':
			print('yes')
			ConsistOf.objects.create(gid=group,username=request.user)
			return JsonResponse("Cancel request",safe=False)
		else:
			print('no')
			ConsistOf.objects.filter(gid=group,username=request.user).delete()
			return JsonResponse("Request To join",safe=False)

def AdminAddQueueMembers(request):
	if request.is_ajax() and request.method=='POST':
		gid=request.POST['id']
		username=request.POST['username']

		group=get_object_or_404(Groups,id=gid)
		user=get_object_or_404(User,username=username)
		ConsistOf.objects.filter(gid=group,username=user).update(confirm=1)
		print(type)
		return JsonResponse(2,safe=False)



def AddMembers(request):
	if request.is_ajax:
		print("here")
		print(request.POST)
		user=request.POST['search_user']
		gid=request.POST['group_id']
		try:
			user=User.objects.get(username=user)
		except:
			print('Not available')
			return JsonResponse(0,safe=False)

		gid=get_object_or_404(Groups,id=gid)
		user=User.objects.get(username=user)
		ConsistOf.objects.create(gid=gid,username=user)
		return JsonResponse(1,safe=False)

class UploadProfile(View):
	def get(self, request):
		user=self.request.username
		ProfileObj=Profile.objects.get(username=User.objects.get(username=user))
		return render(self.request,'user/profile.html', {'ProfileObj':ProfileObj})

	def post(self, request):
		form = Cover(self.request.POST, self.request.FILES)
		if form.is_valid():
			ProfileForm=form.save(commit=False)
			ProfileForm.username=User.objects.get(username=self.request.user.username)
			ProfileForm.title="Updated Profile"
			ProfileForm.privacy='fs'
			ProfileForm.save()
			Notification.objects.create(from_user=request.user,sid=status.objects.get(id=ProfileForm.id),notification_type='P')
			Profile.objects.filter(username=self.request.user).update(sid=Status.objects.get(id=ProfileForm.id))
			obj=Status.objects.get(id=ProfileForm.id)
			data = {'is_valid': True,'url':obj.image.url}
		else:
			data = {'is_valid': False}
		return JsonResponse(data)


class UploadCover(View):
	def post(self, request):
		print("enter")
		form = Cover(self.request.POST, self.request.FILES)
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
	if request.is_ajax() and request.method=='POST':
		print("Nope")
		form=CreateGroup(request.POST)
		if form.is_valid():
			print(form)
			newgroup=form.save(commit=False)
			print('trying')
			form.save()
			group=Groups.objects.get(id=newgroup.id)
			print(newgroup.gname)
			ConsistOf.objects.create(username=request.user,gid=group,gadmin=1,confirm=1)
			data = {'is_valid': True,'gname':group.gname,'gid':group.id}
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
	form=CreateGroup(None)
	return render(request,template_name,{'data':query_set,'form':form})

def create_post(request):
	if request.method=="POST":
		form=CreatePost(request.POST,request.FILES)
		if form.is_valid():
			post=form.save(commit=False)
			post.username=User.objects.get(username=request.user.username)
			post=form.save()
			print(post)
			print(post.id)
			sid=Status.objects.get(id=post.id)
			print(sid)
			Notification.objects.create(from_user=request.user,sid=sid,notification_type='P')

			return redirect('index')
	else:
		form=CreatePost(None)
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
		context['chatusers']=Check_user_online(self.request,self.request.user)
		context=friends_list(self.request,self.request.user.username,context)
		return context

##this is for profile

def UserProfile(request,slug):
	profile=Profile.objects.get(slug=slug)
	chatusers=Check_user_online(request,profile.username)
	friends_suggestion=FriendsOfFriends(request,request.user)
	tempuser=User.objects.filter(username=profile.username)
	for x in tempuser:
		x.status = 'Online' if hasattr(tempuser, 'logged_in_user') else 'Offline'
	y=friendship(request.user,profile.username)
	privacy='NoConnection'
	if request.user ==profile.username:
		posts=user_post(request,request.user,GetUserPosts(request))
		privacy='NoNeed'
	elif profile.username in chatusers:
		privacy='fs'
	elif profile.username in friends_suggestion:
		privacy='fsofs'
	#check all conditions for all privacy

	if privacy=='fsofs':
		chatusers=Check_user_online(request,profile.username)
		friends_suggestion=FriendsOfFriends(request,profile.username)
		loggedInUserFriendsSuggestion=FriendsOfFriends(request,request.user)
		user=User.objects.filter(username=profile.username)
		user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
		UserPostWithPrivacyPublic=Status.objects.filter(username=profile.username,privacy='pbc')


		posts=Status.objects.filter(username__in=friends_suggestion,gid__isnull=True).exclude(privacy='Me').exclude(privacy='fs').select_related('username').order_by('-time')

	elif privacy=='fs':

		chatusers=Check_user_online(request,profile.username)
		friends_suggestion=FriendsOfFriends(request,profile.username)

		usersPost=Status.objects.filter(username=profile.username,gid__isnull=True).exclude(privacy='Me').select_related('username').order_by('-time')
		friendsPostWithoutGroup=Status.objects.filter(username__in=chatusers,gid__isnull=True).exclude(privacy='Me').select_related('username').order_by('-time')##friends Posts
		tempfriendsPostWithGroupPrivacyOpen=Status.objects.filter(username__in=chatusers,gid__isnull=False).exclude(privacy='CL').select_related('username').order_by('-time')
		friendsPostWithGroupPrivacyOpen=Status.objects.none()
		for x in tempfriendsPostWithGroupPrivacyOpen:
			if x.gid.privacy=='OP':
				friendsPostWithGroupPrivacyOpen=friendsPostWithGroupPrivacyOpen|Status.objects.filter(id=x.id)
		posts=usersPost|friendsPostWithoutGroup|friendsPostWithGroupPrivacyOpen
	else:
		#define some post methods here
		chatusers=Check_user_online(request,profile.username)
		userposts=Status.objects.filter(username=profile.username,privacy='pbc').select_related('username').order_by('time')
		friendsPostWithoutGroup=Status.objects.filter(username__in=chatusers,gid__isnull=True).exclude(privacy='Me').select_related('username').order_by('-time')##friends Posts
		posts=userposts|friendsPostWithoutGroup


	chatusers=Check_user_online(request,request.user)# define herebecause it was giving me searched user chatmembers
	posts=user_post(request,profile.username,posts)
	return render(request,'user/profile.html',{'User':profile,'posts':posts,'y':y,'chatusers':chatusers})


def UserFriendsList(request,slug):
	profile=Profile.objects.get(slug=slug)
	chatusers=Check_user_online(request,profile.username)
	friends_suggestion=FriendsOfFriends(request,request.user)
	tempuser=User.objects.filter(username=profile.username)
	for x in tempuser:
		x.status = 'Online' if hasattr(tempuser, 'logged_in_user') else 'Offline'
	y=friendship(request.user,profile.username)


	friends_list=Profile.objects.filter(username__in=chatusers)
	for x in friends_list:
		if str(x.username)==request.user:
			x.y=-1
		else:
			user=request.user
			fuser=x.username
			user_obj=User.objects.get(username=user)
			fuser_obj=User.objects.get(username=fuser)
			x.y=friendship(user_obj,fuser_obj)

	return render(request,'user/partial/friends_list.html',{'User':profile,'y':y,'chatusers':chatusers,'friends_list': friends_list})

def UserPhotos(request,slug):

	profile=Profile.objects.get(slug=slug)
	chatusers=Check_user_online(request,profile.username)
	friends_suggestion=FriendsOfFriends(request,request.user)
	tempuser=User.objects.filter(username=profile.username)
	for x in tempuser:
		x.status = 'Online' if hasattr(tempuser, 'logged_in_user') else 'Offline'
	y=friendship(request.user,profile.username)


	photo_albums = Status.objects.filter(username=profile.username)
	return render(request,'user/partial/photo_frame.html',{'User':profile,'y':y,'chatusers':chatusers,'photo_albums':photo_albums})


def UserProfileEdit(request,slug):
	profile=Profile.objects.get(slug=slug)
	chatusers=Check_user_online(request,profile.username)
	friends_suggestion=FriendsOfFriends(request,request.user)
	tempuser=User.objects.filter(username=profile.username)
	for x in tempuser:
		x.status = 'Online' if hasattr(tempuser, 'logged_in_user') else 'Offline'
	y=friendship(request.user,profile.username)


	if  request.method=='POST':
		form=EditProfileForm(request.POST,instance=request.user.profile)
		if form.is_valid():
			form.save()
			print('do some checks')
			return HttpResponseRedirect(request.path_info)
	else:
		form=EditProfileForm(instance=request.user.profile)
		print(chatusers)
		return render(request,'user/partial/settings.html',{'User':profile,'y':y,'chatusers':chatusers,'form':form})



def UserChangePassword(request,slug):

	profile=Profile.objects.get(slug=slug)
	chatusers=Check_user_online(request,profile.username)
	friends_suggestion=FriendsOfFriends(request,request.user)
	tempuser=User.objects.filter(username=profile.username)
	for x in tempuser:
		x.status = 'Online' if hasattr(tempuser, 'logged_in_user') else 'Offline'
	y=friendship(request.user,profile.username)


	if request.method=='POST':
		form=ChangePasswordForm(request.POST)
		print(form)
		if form.is_valid():
			new_password = form.cleaned_data.get('new_password')
			print('hii')
			user.set_password(new_password)
			print('byee')
			user.save()
			update_session_auth_hash(request, user)
			return HttpResponseRedirect(request.path_info)

	else:

		form=ChangePasswordForm(instance=request.user)
		return render(request,'user/partial/password.html',{'User':profile,'y':y,'chatusers':chatusers,'form':form})


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
			check=CommentLikes.objects.filter(username=User.objects.get(username=username)).filter(cid=Comment.objects.get(id=id))
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

def Messenger_Chatting(request,slug1,slug2):
	profile1=Profile.objects.get(slug=slug1)
	profile2=Profile.objects.get(slug=slug2)
	user_obj=User.objects.get(username=request.user.username)
	fuser_obj=User.objects.get(username=profile2.username)
	friendship=FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj,confirm_request=2,blocked_status=0) |Q(username=fuser_obj,fusername=user_obj,confirm_request=2,blocked_status=0))
	if user_obj !=profile1.username or not friendship.exists():
		return HttpResponse("Something Fishy is going on")

	read_messages=Message.objects.filter(username=fuser_obj,fusername=user_obj,is_read=False).update(is_read=True)
	msg_obj=Message.objects.filter(Q(username=user_obj,fusername=fuser_obj)|Q(username=fuser_obj,fusername=user_obj)).select_related('username').select_related('fusername')

	users=Check_user_online(request,request.user)
	print(users)
	print('hii')
	form=ChattingForm(None)
	print('byee')
	return render(request,'chat/messenger.html',{'msg_obj':msg_obj,'chatusers':users,'fuser_obj':fuser_obj,'form':form})
	return HttpResponse("hello")

def Message_received(request):
	if request.is_ajax() and request.method=='POST':
		print('here')
		fuser_obj=User.objects.get(username=request.POST['fusername'])
		user_obj=request.user
		#clean this data
		text=request.POST['text']
		friendship=FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj,confirm_request=2,blocked_status=0) |Q(username=fuser_obj,fusername=user_obj,confirm_request=2,blocked_status=0))
		if friendship.exists():
			Message.objects.create(username=request.user,fusername=fuser_obj,text=text)
			print('done')
			return JsonResponse(10,safe=False)
		print('nope')
	return JsonResponse(0,safe=False)

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
	if request.is_ajax() and request.method=='POST':
		fuser=request.POST['fuser']
		type=request.POST['type']
		user_obj=User.objects.get(username=request.user)
		fuser_obj=User.objects.get(username=fuser)
		##check again these conditions to make it more secure and reliable
		#not completed
		if request.user==fuser:#this can't happen.Only by some inspect element tools
			return JsonResponse(0,safe=False)
		if type=='Send':
			#check if relationship already exists between users
			obj=FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj))
			if obj.exists():
				print(obj)
				return JsonResponse(0,safe=False)
			FriendsWith.objects.create(username=user_obj,fusername=fuser_obj)
			Notification.objects.create(from_user=user_obj,to_user=fuser_obj,notification_type='SR')
		elif type=='Delete' or type=='Unfriend' or type=='Cancel':
			#write code to update te result
			FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj)).delete()
		elif type=='Confirm':
			FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj)).update(confirm_request=2)
			print('hey')
			Notification.objects.create(from_user=user_obj,to_user=fuser_obj,notification_type='CR')
			print('done')
		else:
			print('hhh')
			return JsonResponse(0,safe=False)
		return JsonResponse(1,safe=False)


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
	return fishy(request)

def EditComments(request):
	if request.is_ajax() and request.method=='POST':
		#do validations that user is the owner of comment or not
		cid=request.POST['cid']
		text=request.POST['post']
		if not text:
			return JsonResponse(0,safe=False)
		try:
			comment=Comment.objects.get(id=cid,username=request.user)
		except ObjectDoesNotExist:
			comment=None
			return JsonResponse(0,safe=False)
		Comment.objects.filter(id=cid,username=request.user).update(text=text)
		print('here')
		comment=Comment.objects.get(id=cid,username=request.user)
		comment.likes=CommentLikes.objects.filter(cid=cid).count()
		data=render_to_string('uposts/partials/editComment.html',{'comment':comment},request)
		return JsonResponse(data,safe=False)
	return fishy(request)



def get_contifications(request):
	if request.is_ajax():
		#Notification.objects.filter(is_read=False).update(is_read=True)
		chatusers=Check_user_online(request,request.user)
		IndividualNotifications=Notification.objects.none()
		for x in chatusers:
			IndividualNotifications=IndividualNotifications|Notification.objects.filter(from_user=x,to_user=request.user,is_read=False)
		print(IndividualNotifications)
		PostNotification=Notification.objects.none()
		for x in chatusers:
			PostNotification=PostNotification|Notification.objects.filter(from_user=x,to_user__isnull=True,is_read=False)
		notifications=((IndividualNotifications|PostNotification)|Notification.objects.filter(to_user=request.user,is_read=False))[:4]
		print(notifications)
		for notification in notifications:
			notification.is_read=True
			notification.save()
		data=render_to_string('notification/last_notifications.html',{'notifications':notifications},request)
		return JsonResponse(data,safe=False)
	else:
		chatusers=Check_user_online(request,request.user)
		IndividualNotifications=Notification.objects.none()
		for x in chatusers:
			IndividualNotifications=IndividualNotifications|Notification.objects.filter(from_user=x,to_user=request.user)
		print(IndividualNotifications)
		PostNotification=Notification.objects.none()
		for x in chatusers:
			PostNotification=PostNotification|Notification.objects.filter(from_user=x,to_user__isnull=True)

		notifications=(IndividualNotifications|PostNotification|Notification.objects.filter(to_user=request.user,is_read=False)).select_related('from_user')
		print(notifications)
		return render(request,"notification/notifications.html",{'notifications':notifications})

	return JsonResponse(1,safe=False)


def check_contification(request):
	if request.is_ajax():
		chatusers=Check_user_online(request,request.user)
		IndividualNotifications=Notification.objects.none()
		for x in chatusers:
			IndividualNotifications=IndividualNotifications|Notification.objects.filter(from_user=x,to_user=request.user,is_read=False)
		print(IndividualNotifications)
		PostNotification=Notification.objects.none()
		for x in chatusers:
			PostNotification=PostNotification|Notification.objects.filter(from_user=x,to_user__isnull=True,is_read=False)

		notifications=(IndividualNotifications|PostNotification)|Notification.objects.filter(to_user=request.user,is_read=False)
		data=len(notifications)
		return JsonResponse(data,safe=False)
