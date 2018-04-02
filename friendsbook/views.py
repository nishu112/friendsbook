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
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import datetime


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
	for x in chatusers:
		x.status = 'Online' if hasattr(x, 'logged_in_user') else 'Offline'
		x.noOf_unread=int(Message.objects.filter(username=x,fusername=user,is_read=False).count())
		##print(x, user,x.noOf_unread)
	return chatusers

def Check_user_Username(request,user):
	obj1=FriendsWith.objects.filter(username=user,confirm_request=2,blocked_status=0).select_related('fusername').values('fusername')
	obj1=User.objects.filter(id__in=obj1).values('username')
	obj2=FriendsWith.objects.filter(fusername=user,confirm_request=2,blocked_status=0).select_related('username').values('username')
	obj2=User.objects.filter(id__in=obj2).values('username')
	obj=obj1 | obj2
	return obj


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
		if ( user_form.is_valid() and profile_form.is_valid() ):
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

def education(request):
	if request.method=='POST':
		details=EducationDetails(request.POST)
		print('got here')
		if details.is_valid():
			education=details.save(commit=False)
			education.username=request.user
			education.save()
			return redirect('workDetail')
		else:
			return render(request,"user/educationDetails.html",{'form':form})
	else:
		#return redirect('index')
		print('yes')
		form=EducationDetails(None)
		print('nope')
		return render(request,"user/educationDetails.html",{'form':form})

def workingProfile(request):
	#return redirect('index')
	if request.method=='POST':
		details=WorkingFor(request.POST)
		print('got here')
		if details.is_valid():
			education=details.save(commit=False)
			education.username=request.user
			education.save()
			return redirect('index')
		else:
			return render(request,"user/educationDetails.html",{'form':form})
	else:
		print('yes')
		form=WorkingFor(None)
		print('nope')
		return render(request,"user/working.html",{'form':form})

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
			epsilon='0:10:60.000000'
			diff=datetime.datetime.now()-request.user.date_joined
			print(datetime.datetime.now())
			print(request.user.date_joined)
			print(diff)
			if str(diff)<epsilon:
				return redirect('educationDetails')
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

POSTS_NUM_PAGES = 4

def GetUserPosts(request):
	chatusers=Check_user_online(request,request.user)
	friends_suggestion=FriendsOfFriends(request,request.user)
	user=User.objects.filter(username=request.user)
	user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
	friendsAndMe=chatusers|user


	friends_suggestion=User.objects.filter(id__in=friends_suggestion).exclude(id__in=friendsAndMe)
	friendsPostWithoutGroup=Status.objects.filter(username__in=chatusers,gid__isnull=True).exclude(privacy='me').select_related('username').order_by('-time')##friends Posts
	tempfriendsPostWithGroupPrivacyOpen=Status.objects.filter(username__in=chatusers,gid__isnull=False).select_related('username').order_by('-time')
	friendsPostWithGroupPrivacyOpen=Status.objects.none()
	UserPartOfGroup=ConsistOf.objects.filter(username=request.user,confirm=1).values('gid')
	PostOfUserPartOfGroup=Status.objects.filter(gid__in=UserPartOfGroup)
	for x in tempfriendsPostWithGroupPrivacyOpen:
		if x.gid.privacy=='OP':
			friendsPostWithGroupPrivacyOpen=friendsPostWithGroupPrivacyOpen|Status.objects.filter(id=x.id)
	myPosts=Status.objects.filter(username=request.user).select_related('username').order_by('-time')
	friendsOfFriendsPosts=Status.objects.filter(username__in=friends_suggestion,gid__isnull=True).exclude(privacy='me').exclude(privacy='fs').select_related('username').order_by('-time')
	posts=friendsPostWithoutGroup|friendsPostWithGroupPrivacyOpen|myPosts|friendsOfFriendsPosts|PostOfUserPartOfGroup
    #from_feed = -1
    #if allposts:
    #    from_feed = feeds[0].id
	return posts

#load on timeline posts for ajax call

def GetUserPostsByAjax(request):
	page = request.GET.get('page')
	group=request.GET.get('groupid')

	user=request.GET.get('requestuser')
	#print(page)
	#print('came here')
	#check validations that requested user is connected to a group or not
	#print(group)
	#print(user)
	if user:
		#print('ok')
		#print(user)
		user=get_object_or_404(User, username=user)


		#print('got user')
		try:
			profile=Profile.objects.get(username=user)
		except ObjectDoesNotExist:
			return JsonResponse(0,safe=False)
		#print('came')
		chatusers=Check_user_online(request,profile.username)
		friends_suggestion=FriendsOfFriends(request,profile.username)
		tempuser=User.objects.filter(username=profile.username)

		y=friendship(request.user,profile.username)
		privacy='NoConnection'
		#LoggedInUser=User.objects.get(username=request.user.username)
		#print(type(request.user))
		#print(type(profile.username))
		#print(chatusers)
		for x in chatusers:
			if str(request.user.username)==str(x.username):
				privacy='fs'
				#print('fs')
		friends_suggestion=friends_suggestion.exclude(username=User.objects.get(username=profile.username))
		#queryset.exclude(lugar="Quito")
		#print(friends_suggestion)
		if request.user ==profile.username:
			posts=user_post(request,request.user,GetUserPosts(request))
			#print(posts)
			privacy='NoNeed'
		elif request.user in friends_suggestion and privacy!='fs':
			privacy='fsofs'
		#check all conditions for all privacy
		#print(privacy)
		#print('checking')
		#print('checking')
		PusersFriends=Check_user_online(request,profile.username)
		LoggedInUserFriends=Check_user_online(request,request.user)
		##print(chatusers)
		#print(profile.username)
		if privacy=='fsofs':
			#chatusers=Check_user_online(request,profile.username)
			commonFriends=PusersFriends&LoggedInUserFriends
			#print(PusersFriends)
			#print(LoggedInUserFriends)
			#print(commonFriends)
			#userExceptCommonFriends=PusersFriends-commonFriends

			CommonFriendsPosts=Status.objects.filter(Q(username__in=commonFriends,gid__isnull=True)).exclude(privacy='me').exclude(privacy='fs')
			#PostsOfUserFriendsExcludeCommonFriends=Status.objects.filter(Q(username__in=PusersFriends,gid__isnull=True)).exclude(username__in=commonFriends)
			#update
			##print(CommonFriendsPosts)
			UserPostWithPrivacyPublic=Status.objects.filter(username=profile.username,gid__isnull=True).exclude(privacy='me').exclude(privacy='fs')
			LoggedInUserPosts=Status.objects.filter(username=request.user,gid__isnull=True).exclude(privacy='me').exclude(privacy='fs')
			PuserFriendsWithoutCommon=Status.objects.filter(username__in=PusersFriends,gid__isnull=True,privacy='Pbc')
			posts=CommonFriendsPosts|PuserFriendsWithoutCommon|LoggedInUserPosts|UserPostWithPrivacyPublic


		elif privacy=='fs':

			#chatusers=Check_user_online(request,profile.username)
			commonFriends=PusersFriends&LoggedInUserFriends
			mutualFriendsPosts=Status.objects.filter(username__in=commonFriends,gid__isnull=True).exclude(privacy='me').order_by('-time')
			PuserFriendsPosts=Status.objects.filter(username__in=PusersFriends,gid__isnull=True).exclude(privacy='me').exclude(privacy='fs').order_by('-time')
			LoggedInUserPosts=Status.objects.filter(username=request.user,gid__isnull=True).exclude(privacy='me').order_by('-time')

			PuserPosts=Status.objects.filter(username=profile.username,gid__isnull=True).exclude(privacy='me')

			posts=LoggedInUserPosts|PuserFriendsPosts|mutualFriendsPosts|PuserPosts
		elif privacy=='NoConnection':
			#define some post methods here
			userposts=Status.objects.filter(username=profile.username,gid__isnull=True,privacy='Pbc').select_related('username').order_by('time')
			FriendsPostsWithPublicPrivacy=Status.objects.filter(username__in=PusersFriends,gid__isnull=True,privacy='Pbc')
			posts=userposts|FriendsPostsWithPublicPrivacy

		#group posts a users can see on anyone profile
		#common groups
		PuserGroupPostWithClosedPrivacy=ConsistOf.objects.filter(username=profile.username).select_related('gid').values('gid')
		LoggedInUserGroupsWithClosedPrivacy=ConsistOf.objects.filter(username=request.user).select_related('gid').values('gid')
		commonGroups=PuserGroupPostWithClosedPrivacy&LoggedInUserGroupsWithClosedPrivacy
		PuserGroupPost=Status.objects.filter(gid__in=commonGroups,username=profile.username).order_by('-time')
		#PuserGroupWithOpenPrivacy=ConsistOf.objects.filter(username=profile.username)
		#PuserGroupWithOpenPrivacy=ConsistOf.objects.none().select_related('gid').values('gid')
		#print(commonGroups)
		#print('commonthzhfghxfh')
		PuserGroupsWithOpenPrivacy=Groups.objects.filter(id__in=PuserGroupPostWithClosedPrivacy,privacy='OP').values('id')

		PuserGroupPostWithOpenPrivacy=Status.objects.filter(username=profile.username,gid__in=PuserGroupsWithOpenPrivacy).order_by('-time')
		posts=posts|PuserGroupPost|PuserGroupPostWithOpenPrivacy
		if privacy!='NoNeed':
			posts=user_post(request,request.user,posts)


		#code to load post and using the privacy features
	elif group is None:
		#print("doesn't exists")
		postsOfUserExcludingGroupPosts=GetUserPosts(request)
		#print('begin')
		##print(chatusers)
		UserPartOfGroup=ConsistOf.objects.filter(username=request.user,confirm=1).values('gid')
		##print(postsOfUserExcludingGroupPosts)
		#print('done')
		GroupFeeds=Status.objects.filter(gid__in=UserPartOfGroup).order_by('-time')
		##print(GroupFeeds)
		posts=postsOfUserExcludingGroupPosts|GroupFeeds
		posts=user_post(request,request.user,posts)
		##print(posts)

	else:
		#print('exists ')
		UserPartOfGroup=ConsistOf.objects.filter(username=request.user,confirm=1).values('gid')
		##print(UserPartOfGroup)
		GroupFeeds=Status.objects.filter(gid=group).order_by('-time')
		#print(GroupFeeds)
		print('done')
		posts=GroupFeeds
		posts=user_post(request,request.user,posts)

	##print(page," ok")

	##print('here')
	all_posts = posts
	paginator = Paginator(all_posts, POSTS_NUM_PAGES)
	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		return HttpResponseBadRequest()
	except EmptyPage:
		posts = []
	if(len(posts)==0):
		return JsonResponse(0,safe=False)
	##print('done ',posts)
	#posts = paginator.page(page)
	ajax_posts=render_to_string('uposts/partials/ajax_only_post.html', {'posts':posts},request)
	##print('contents')
	##print(ajax_posts)
	return JsonResponse(ajax_posts,safe=False)

def home(request):

	chatusers=Check_user_online(request,request.user)
	user=User.objects.filter(username=request.user)
	user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
	friends_suggestion=FriendsOfFriends(request,request.user)
	friendsAndMe=chatusers|user
	friends_suggestion=User.objects.filter(id__in=friends_suggestion).exclude(id__in=friendsAndMe)
	postsOfUserExcludingGroupPosts=GetUserPosts(request)
	#print('begin')
	#print(chatusers)
	UserPartOfGroup=ConsistOf.objects.filter(username=request.user,confirm=1).values('gid')
	#print(postsOfUserExcludingGroupPosts)
	GroupFeeds=Status.objects.filter(gid__in=UserPartOfGroup).order_by('-time')
	#print(GroupFeeds)
	posts=postsOfUserExcludingGroupPosts|GroupFeeds
	posts=user_post(request,request.user,posts)
	#print(posts)


	all_posts = posts
	paginator = Paginator(all_posts, POSTS_NUM_PAGES)
	posts = paginator.page(1)
	groups=group_list(request)
	#print(friends_suggestion)
	#print(friends_suggestion[0:1])
	pending_request=FriendsWith.objects.filter(fusername=request.user,confirm_request=1)
	print('okk')

	return render(request,"home/index.html",{'posts':posts,'page':1,'chatusers':chatusers,'groups':groups,'friends_suggestion':friends_suggestion[0:10],'pending_request':pending_request[0:10],'newGroupForm':CreateGroup(None)})

def getSinglePost(request):
	if request.is_ajax():
		id=request.GET.get('id')

		status=Status.objects.get(id=id)
		#chatusers=Check_user_online(request,request.user)
		#user=User.objects.filter(username=request.user)
		#user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
		#friends_suggestion=FriendsOfFriends(request,request.user)
		#friendsAndMe=chatusers|user
		#friends_suggestion=User.objects.filter(id__in=friends_suggestion).exclude(id__in=friendsAndMe)
		status.likes=StatusLikes.objects.filter(sid=status).count()
		status.comments=Comment.objects.filter(sid=status).count()
		status.is_like=StatusLikes.objects.filter(username=request.user,sid=status).count()
		content=render_to_string('uposts/posts.html',{'status':status},request)
		return JsonResponse(content,safe=False)


def PostDetailView(request,slug):
	##print('hii')
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
		#print('post form')
		form=CreateGroupPost(request.POST,request.FILES)
		if form.is_valid():
			#print('Hii')
			post=form.save(commit=False)
			post.username=User.objects.get(username=request.user.username)
			post.title="posted in "
			post.gid=group
			post=form.save()
			#print('okk')
			#print(ConsistOf.objects.all()[0:1].values('username'))
			groupMembers=ConsistOf.objects.filter(gid=group,confirm=1).exclude(username=request.user).select_related('username').values('username')
			#print(groupMembers)
			#print('okk2')
			for x in groupMembers:
				Notification.objects.create(from_user=request.user,to_user_id=x['username'],gid=group,notification_type='PG')
			#Notification.objects.create(from_user=request.user,gid=group,notification_type='PG')
		return HttpResponseRedirect(request.path_info)
		#print('byee')

	else:
		form =CreateGroupPost(None)
		#check user have the permission to access this group
		#only then user able to access this method
		posts=Status.objects.filter(gid=group).select_related('username').order_by('-time')
		posts=user_post(request,request.user,posts)
		all_posts = posts
		paginator = Paginator(all_posts, POSTS_NUM_PAGES)
		posts = paginator.page(1)

		chatusers=Check_user_online(request,request.user)
		try:
		    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
		except ObjectDoesNotExist:
		    group_consist=None

		return render(request,"groups/index.html",{'posts':posts,'page':1,'group':group,'form':form,'chatusers':chatusers,'group_consist':group_consist})

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
	#print(chatusers)
	members=ConsistOf.objects.filter(gid=group,gadmin=0,confirm=1).select_related('username')
	admins=ConsistOf.objects.filter(gid=group,gadmin=1).select_related('username')
	try:
	    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
	except ObjectDoesNotExist:
	    group_consist=None

	#print(group_consist)
	return render(request,"groups/partial/group_members.html",{'group_members':members,'group':group,'chatusers':chatusers,'admins':admins,'group_consist':group_consist,'group_consist':group_consist})

def GroupsPhotos(request,pk):
	group=get_object_or_404(Groups, id=pk)
	#use paginartor to show all photos
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
	#print('Hii')

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
	#print(chatusers)
	members=ConsistOf.objects.filter(gid=group,gadmin=0,confirm=1).select_related('username')
	admins=ConsistOf.objects.filter(gid=group,gadmin=1).select_related('username')
	try:
	    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
	except ObjectDoesNotExist:
	    group_consist=None


	if request.method=='POST':
		#print('coming to settings cahnges')
		form=CreateGroup(request.POST,instance=group)
		#print('coming to settings')
		if form.is_valid():
			#print('dnoe')
			form.save()
		else:
			return render(request,"groups/partial/settings.html",{'group':group,'chatusers':chatusers,'group_consist':group_consist,'form':form})
		return redirect('AboutGroup',group.id)
	else:
		#print('ok till here')
		form=CreateGroup(instance=group)
		return render(request,"groups/partial/settings.html",{'group':group,'chatusers':chatusers,'group_consist':group_consist,'form':form})


def EditAboutGroupInfo(request,pk):
	group=get_object_or_404(Groups, id=pk)
	#print('Hii')

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
	#print(chatusers)
	members=ConsistOf.objects.filter(gid=group,gadmin=0,confirm=1).select_related('username')
	admins=ConsistOf.objects.filter(gid=group,gadmin=1).select_related('username')
	try:
	    group_consist=ConsistOf.objects.get(gid=group,username=request.user,confirm=1)
	except ObjectDoesNotExist:
	    group_consist=None


	if request.method=='POST':
		#print('coming to post')
		form=EditAboutGroup(request.POST,instance=group)
		#print('coming to post')
		if form.is_valid():
			about=request.POST['about']
			Groups.objects.filter(id=pk).update(about=about)
		return redirect('AboutGroup',group.id)
	else:
		#print('ok till here')
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
	#print(pendingrequests)
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
		#print('Hello')
		#print(username)
		#print('Here')

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
		#print(content)
		return JsonResponse(content,safe=False)

def UploadGroupCover(request):
	if request.is_ajax and request.method=='POST':
		#print("insife")
		form=Cover(request.POST,request.FILES)
		#print(request.POST)
		gid=request.POST['gid']
		group=get_object_or_404(Groups,id=gid)
		if form.is_valid():
			cover=form.save(commit=False)
			cover.username=request.user
			cover.title="Posted in "
			cover.gid=group
			##correct this behavior right now only changing cover for a specific group
			cover.save()
			groupMembers=ConsistOf.objects.filter(gid=group,confirm=1).exclude(username=request.user).select_related('username').values('username')
			for x in groupMembers:
				Notification.objects.create(from_user=request.user,to_user_id=x['username'],gid=group,notification_type='PG')
			#Notification.objects.create(from_user=request.user,gid=group,notification_type='PG')
			sid=Status.objects.get(id=cover.id)
			Groups.objects.filter(id=gid).update(cover=sid)
			gid=Groups.objects.get(id=gid)
			obj=Status.objects.get(id=cover.id)
			data = {'is_valid': True,'url':obj.image.url}
		else:
			data = {'is_valid': False}
		#print("ok")
		return JsonResponse(data,safe=False)

def joinrequest(request):
	if request.is_ajax and request.method=='POST':
		gid=request.POST['id']
		data=request.POST['data']
		#print(gid)
		#print(data)
		group=get_object_or_404(Groups,id=gid)
		if data=='Request To join':
			#print('yes')
			ConsistOf.objects.create(gid=group,username=request.user)
			return JsonResponse("Cancel request",safe=False)
		else:
			#print('no')
			ConsistOf.objects.filter(gid=group,username=request.user).delete()
			return JsonResponse("Request To join",safe=False)

def AdminAddQueueMembers(request):
	if request.is_ajax() and request.method=='POST':
		gid=request.POST['id']
		username=request.POST['username']

		group=get_object_or_404(Groups,id=gid)
		user=get_object_or_404(User,username=username)
		ConsistOf.objects.filter(gid=group,username=user).update(confirm=1)
		#print(type)
		return JsonResponse(2,safe=False)



def AddMembers(request):
	if request.is_ajax:
		#print("here")
		#print(request.POST)
		user=request.POST['search_user']
		gid=request.POST['group_id']
		try:
			user=User.objects.get(username=user)
		except:
			#print('Not available')
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
			status=ProfileForm.save()
			print(ProfileForm)
			print(ProfileForm.id)
			sid=ProfileForm
			friends=giveFriendsUsername(request,request.user)
			#print('done2')
			for x in friends:
				Notification.objects.create(from_user=request.user,to_user=x,sid=sid,notification_type='P')
			#Notification.objects.create(from_user=request.user,sid=Status.objects.get(id=ProfileForm.id),notification_type='P')
			Profile.objects.filter(username=self.request.user).update(sid=Status.objects.get(id=ProfileForm.id))
			obj=Status.objects.get(id=ProfileForm.id)
			data = {'is_valid': True,'url':obj.image.url}
		else:
			data = {'is_valid': False}
		return JsonResponse(data)


class UploadCover(View):
	def post(self, request):
		#print("enter")
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
		#print("Nope")
		form=CreateGroup(request.POST)
		if form.is_valid():
			#print(form)
			newgroup=form.save(commit=False)
			#print('trying')
			form.save()
			group=Groups.objects.get(id=newgroup.id)
			#print(newgroup.gname)
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


def giveFriendsUsername(request,user):
	obj1=FriendsWith.objects.filter(username=user,confirm_request=2,blocked_status=0).select_related('fusername').values('fusername')
	obj1=User.objects.filter(id__in=obj1)
	obj2=FriendsWith.objects.filter(fusername=user,confirm_request=2,blocked_status=0).select_related('username').values('username')
	obj2=User.objects.filter(id__in=obj2)
	obj=obj1 | obj2
	return obj


def create_post(request):
	if request.method=="POST":
		form=CreatePost(request.POST,request.FILES)
		if form.is_valid():
			post=form.save(commit=False)
			post.username=User.objects.get(username=request.user.username)
			post=form.save()
			#print(post)
			#print(post.id)
			sid=Status.objects.get(id=post.id)
			#print(sid)
			friends=giveFriendsUsername(request,request.user)
			#print('done2')
			for x in friends:
				Notification.objects.create(from_user=request.user,to_user=x,sid=sid,notification_type='P')
			#print(friends)
			#print('done')
			#Notification.objects.create(from_user=request.user,sid=sid,notification_type='P')

			return redirect('index')
	else:
		form=CreatePost(None)
	return render(request,"uposts/post_create.html",{'form':form})

Friends_Per_Page=5

def LoadFriendsListViaAjax(request):
	page = request.GET.get('page')
	fname=request.GET.get('search_user')
	#Profile.objects.filter(Q(fname__istartswith=fname) | Q(lname__istartswith=fname)).select_related('username').select_related('sid')

	all_friends=Profile.objects.filter(Q(fname__istartswith=fname) | Q(lname__istartswith=fname)).select_related('username').select_related('sid')
	context=friends_list(self.request,self.request.user.username,context)

	addfriends_list=list()
	searched_by=self.request.user.username
	for x in all_friends:
		if str(x.username)==searched_by:
			addfriends_list.append(-1)
		else:
			user=searched_by
			fuser=x.username
			user_obj=User.objects.get(username=user)
			fuser_obj=User.objects.get(username=fuser)
			addfriends_list.append(friendship(user_obj,fuser_obj))
	all_friends=zip(all_friends,addfriends_list)
	paginator = Paginator(all_friends, Friends_Per_Page)

	try:
		friends = paginator.page(page)
	except PageNotAnInteger:
		return HttpResponseBadRequest()
	except EmptyPage:
		friends = []
	if(len(friends)==0):
		return JsonResponse(0,safe=False)

	content=render_to_string('Ajax_load_SearchFriendList.html', {'data': friends},request)
	#print(content)
	return JsonResponse(content,safe=False)

def SearchGroup(request,val):
	print(val)
	return Groups.objects.filter(Q(gname__istartswith=val))


def combineFriendshipDetailwithUsers(request,users):
	addfriends_list=list()
	searched_by=request.user.username
	for x in users:
		if str(x.username)==searched_by:
			addfriends_list.append(-1)
		else:
			user=searched_by
			fuser=x.username
			user_obj=User.objects.get(username=user)
			fuser_obj=User.objects.get(username=fuser)
			addfriends_list.append(friendship(user_obj,fuser_obj))
	return zip(users,addfriends_list)

def advanceSearch(request):
	if request.method=='GET':
		form=advanceSearchForm(request.GET)
		if form.is_valid():
			print('got here')
			name=request.GET.get('name')
			#InstituteName=request.GET.get('InstituteName')
			InstituteName=request.GET.get('InstituteName')
			print(InstituteName,end=' dgdfg')
			courseName=request.GET.get('courseName')
			profile=request.GET.get('profile')
			location=request.GET.get('location')
			print(name)
			print(InstituteName)
			print(courseName)
			print(profile)
			print(location)
			users=Profile.objects.filter(Q(fname__istartswith=name) | Q(lname__istartswith=name)).select_related('username').select_related('sid')
			usernamesEducation=Education.objects.filter(Q(institute_name__istartswith=InstituteName) & Q(course_class__istartswith=courseName)).values('username')
			users1=Profile.objects.filter(username__in=usernamesEducation)
			usernamesWorking=Working.objects.filter(Q(profile__istartswith=profile) &Q(location__istartswith=location) ).values('username')
			print('before')
			users2=Profile.objects.filter(username__in=usernamesWorking)
			username=users1 & users2
			print('After')
			users=users & username
			#users=users & Profile.objects.filter(username__in=username)
			#users=Profile.objects.all()

			users=combineFriendshipDetailwithUsers(request,users)
			groups=SearchGroup(request,name)

			return render(request,'user/advance_search_user.html',{'data':users,'sgroups':groups})
		return render(request,'user/advance_search_user.html')

class FriendsView(generic.ListView):  ###print friendlist of user here
	template_name='user/search_user.html'
	context_object_name='data'

	def get_queryset(self):
		#print('heresbfifb')
		if self.request.method=="GET" :
			fname = self.request.GET.get('search_user')
			#print('hey')
			searchVal=fname
			#print('hey')
			return Profile.objects.filter(Q(fname__istartswith=fname) | Q(lname__istartswith=fname)).select_related('username').select_related('sid')

	def get_context_data(self,**kwargs):
		context=super(FriendsView,self).get_context_data(**kwargs)
		#print(self.request.GET.get('search_user'))
		#print('no')
		print(self.request.method)
		print(self.request.GET.get('search_user'))
		print('doneljsfljn')
		context['sgroups']=SearchGroup(self.request,self.request.GET.get('search_user'))
		print(context['sgroups'])


		context['chatusers']=Check_user_online(self.request,self.request.user)
		#print(context['chatusers'])
		##print(posts)
		#all_friends=context['data']
		#paginator = Paginator(all_friends, Friends_Per_Page)
		#friends = paginator.page(1)
		#context['data']=friends
		#context['page']
		##print(context['data'])


		context['newGroupForm']=CreateGroup(None)

		context['groups']=group_list(self.request)
		context['advanceSearchForm']=advanceSearchForm()

		context=friends_list(self.request,self.request.user.username,context)
		return context

##this is for profile

def UserProfile(request,slug):
	profile=Profile.objects.get(slug=slug)
	chatusers=Check_user_online(request,profile.username)
	friends_suggestion=FriendsOfFriends(request,profile.username)
	tempuser=User.objects.filter(username=profile.username)
	workprofile=Working.objects.filter(username=profile.username).order_by('-WorkingFrom')[0:1]
	educationprofile=Education.objects.filter(username=profile.username).order_by('-date')[0:1]
	for x in tempuser:
		x.status = 'Online' if hasattr(tempuser, 'logged_in_user') else 'Offline'



	y=friendship(request.user,profile.username)
	privacy='NoConnection'
	#LoggedInUser=User.objects.get(username=request.user.username)
	#print(type(request.user))
	#print(type(profile.username))
	#print(chatusers)
	for x in chatusers:
		if str(request.user.username)==str(x.username):
			privacy='fs'
			#print('fs')
	friends_suggestion=friends_suggestion.exclude(username=User.objects.get(username=profile.username))
	#queryset.exclude(lugar="Quito")
	#print(friends_suggestion)
	if request.user ==profile.username:
		posts=user_post(request,request.user,GetUserPosts(request))
		#print(posts)
		privacy='NoNeed'
	elif request.user in friends_suggestion and privacy!='fs':
		privacy='fsofs'
	#check all conditions for all privacy
	#print(privacy)
	#print('checking')
	#print('checking')
	PusersFriends=Check_user_online(request,profile.username)
	LoggedInUserFriends=Check_user_online(request,request.user)
	##print(chatusers)
	#print(profile.username)
	if privacy=='fsofs':
		#chatusers=Check_user_online(request,profile.username)
		commonFriends=PusersFriends&LoggedInUserFriends
		#print(PusersFriends)
		#print(LoggedInUserFriends)
		#print(commonFriends)
		#userExceptCommonFriends=PusersFriends-commonFriends

		CommonFriendsPosts=Status.objects.filter(Q(username__in=commonFriends,gid__isnull=True)).exclude(privacy='me').exclude(privacy='fs')
		#PostsOfUserFriendsExcludeCommonFriends=Status.objects.filter(Q(username__in=PusersFriends,gid__isnull=True)).exclude(username__in=commonFriends)
		#update
		##print(CommonFriendsPosts)
		UserPostWithPrivacyPublic=Status.objects.filter(username=profile.username,gid__isnull=True).exclude(privacy='me').exclude(privacy='fs')
		LoggedInUserPosts=Status.objects.filter(username=request.user,gid__isnull=True).exclude(privacy='me').exclude(privacy='fs')
		PuserFriendsWithoutCommon=Status.objects.filter(username__in=PusersFriends,gid__isnull=True,privacy='Pbc')
		posts=CommonFriendsPosts|PuserFriendsWithoutCommon|LoggedInUserPosts|UserPostWithPrivacyPublic


	elif privacy=='fs':

		#chatusers=Check_user_online(request,profile.username)
		commonFriends=PusersFriends&LoggedInUserFriends
		#print('common friends')
		#print(c`ommonFriends)
		mutualFriendsPosts=Status.objects.filter(username__in=commonFriends,gid__isnull=True).exclude(privacy='me').order_by('-time')
		PuserFriendsPosts=Status.objects.filter(username__in=PusersFriends,gid__isnull=True).exclude(privacy='me').exclude(privacy='fs').order_by('-time')
		LoggedInUserPosts=Status.objects.filter(username=request.user,gid__isnull=True).exclude(privacy='me').order_by('-time')
		PuserPosts=Status.objects.filter(username=profile.username,gid__isnull=True).exclude(privacy='me')
		posts=LoggedInUserPosts|PuserFriendsPosts|mutualFriendsPosts|PuserPosts
	elif privacy=='NoConnection':
		#define some post methods here
		userposts=Status.objects.filter(username=profile.username,gid__isnull=True,privacy='Pbc').select_related('username').order_by('time')
		FriendsPostsWithPublicPrivacy=Status.objects.filter(username__in=PusersFriends,gid__isnull=True,privacy='Pbc')
		posts=userposts|FriendsPostsWithPublicPrivacy

	#group posts a users can see on anyone profile
	#common groups
	PuserGroupPostWithClosedPrivacy=ConsistOf.objects.filter(username=profile.username,confirm=1).values('gid')
	LoggedInUserGroupsWithClosedPrivacy=ConsistOf.objects.filter(username=request.user,confirm=1).values('gid')
	commonGroups=PuserGroupPostWithClosedPrivacy & LoggedInUserGroupsWithClosedPrivacy
	#print(LoggedInUserGroupsWithClosedPrivacy)
	#print(PuserGroupPostWithClosedPrivacy)
	#print(commonGroups)
	#print('hello')
	PuserGroupPost=Status.objects.filter(gid__in=commonGroups,username=profile.username).order_by('-time')
	#PuserGroupWithOpenPrivacy=ConsistOf.objects.filter(username=profile.username)
	#PuserGroupWithOpenPrivacy=ConsistOf.objects.none().select_related('gid').values('gid')
	PuserGroupsWithOpenPrivacy=Groups.objects.filter(id__in=PuserGroupPostWithClosedPrivacy,privacy='OP').values('id')

	PuserGroupPostWithOpenPrivacy=Status.objects.filter(username=profile.username,gid__in=PuserGroupsWithOpenPrivacy).order_by('-time')
	posts=posts|PuserGroupPost|PuserGroupPostWithOpenPrivacy
	#paginator
	all_posts = posts
	paginator = Paginator(all_posts, POSTS_NUM_PAGES)
	posts = paginator.page(1)

	posts=user_post(request,profile.username,posts)


	chatusers=Check_user_online(request,request.user)# define herebecause it was giving me searched user chatmembers
	userPartOfGroups=ConsistOf.objects.filter(username=profile.username,confirm=1)
	print(userPartOfGroups)
	print('okkk')
	print(educationprofile)
	print(workprofile)
	for x in workprofile:
		print(x.WorkingFrom)
		print(x.username)

	return render(request,'user/profile.html',{'User':profile,'page':1,'posts':posts,'y':y,'chatusers':chatusers,'userPartOfGroups':userPartOfGroups,'workprofile':workprofile,'educationprofile':educationprofile})


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
			#print('do some checks')
			return HttpResponseRedirect(request.path_info)
		else:
			return render(request,'user/partial/settings.html',{'User':profile,'y':y,'chatusers':chatusers,'form':form})
	else:
		form=EditProfileForm(instance=request.user.profile)
		#print(chatusers)
		return render(request,'user/partial/settings.html',{'User':profile,'y':y,'chatusers':chatusers,'form':form})



def UserChangePassword(request,slug):

	profile=Profile.objects.get(slug=slug)
	chatusers=Check_user_online(request,profile.username)
	friends_suggestion=FriendsOfFriends(request,request.user)
	tempuser=User.objects.filter(username=profile.username)
	y=friendship(request.user,profile.username)


	if request.method=='POST':
		form=ChangePasswordForm(request.POST)
		print('inside')
		if form.is_valid():
			new_password = form.cleaned_data.get('new_password')
			#print('hii')
			user=request.user
			user.set_password(new_password)
			#print('byee')
			user.save()
			print('ok')
			update_session_auth_hash(request, user)
			return render(request,'user/partial/password.html',{'User':profile,'y':y,'chatusers':chatusers,'form':form,'message':1})
		else:
			return render(request,'user/partial/password.html',{'User':profile,'y':y,'chatusers':chatusers,'form':form})

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
	print('got this')
	username = request.GET.get('username', None)
	data = {
		'is_taken': User.objects.filter(username__iexact=username).exists()
	}
	print(data)
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
			status=Status.objects.get(id=id)
			if not check.exists():
				##print("inside")
				likes=likes+1
				Status.objects.filter(id=id).update(likes=likes)
				if status.username != request.user:
					print('yes')
					Notification.objects.create(from_user=request.user,to_user=status.username,sid=status,notification_type='L')
				like=StatusLikes(username=User.objects.get(username=username),sid=Status.objects.get(id=id))
				like.save()
			else:
				likes=likes-1
				Status.objects.filter(id=id).update(likes=likes)
				if status.username!=request.user:
					Notification.objects.get(from_user=request.user,to_user=status.username,sid=status,notification_type='L').delete()
				StatusLikes.objects.filter(username=User.objects.get(username=username),sid=Status.objects.get(id=id)).delete()
			return HttpResponse(likes)
		if type=="Comment_like":
			check=CommentLikes.objects.filter(username=User.objects.get(username=username)).filter(cid=Comment.objects.get(id=id))
			likes=Comment.objects.get(id=id).likes
			#print('calculated')
			comment=Comment.objects.get(id=id)
			if not check.exists():
				##print("inside")
				likes=likes+1
				Comment.objects.filter(id=id).update(likes=likes)
				if request.user!=comment.username:
					print('done')
					Notification.objects.create(from_user=request.user,to_user=comment.username,sid=comment.sid,notification_type='CL')
				like=CommentLikes(username=User.objects.get(username=username),cid=Comment.objects.get(id=id))

				like.save()
			else:
				likes=likes-1
				Comment.objects.filter(id=id).update(likes=likes)

				if request.user!=comment.username:
					print('undone')
					Notification.objects.create(from_user=request.user,to_user=comment.username,sid=comment.sid,notification_type='CL').delete()
				CommentLikes.objects.filter(username=User.objects.get(username=username),cid=Comment.objects.get(id=id)).delete()
			#print(likes)
			#print('check')
			return HttpResponse(likes)

#ajax
def deleteCommentPost(request):
	if request.is_ajax():
		id=request.POST['id']
		type=request.POST['type']
		#print(id)
		#print('trying')
		#print(type)
		if type=='delete_comment':
			Comment.objects.get(id=id).delete()
			#print('Comment deleted')
		if type=='delete_status':
			Status.objects.get(id=id).delete()
			#print('status deleted')
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
	#print(user_obj)
	#print(fuser_obj)
	#print(Message.objects.filter(username=fuser_obj,fusername=user_obj,is_read=False))
	read_messages=Message.objects.filter(username=fuser_obj,fusername=user_obj,is_read=False).update(is_read=True)
	#print(read_messages)
	msg_obj=Message.objects.filter(Q(username=user_obj,fusername=fuser_obj)|Q(username=fuser_obj,fusername=user_obj)).select_related('username').select_related('fusername').order_by('time')

	users=Check_user_online(request,request.user)
	form=ChattingForm(None)
	return render(request,'chat/messenger.html',{'msg_obj':msg_obj,'chatusers':users,'userProfile':profile1,'fuser_obj':fuser_obj,'form':form})



def Message_received(request):
	if request.is_ajax() and request.method=='POST':
		#print('here')
		fuser_obj=User.objects.get(username=request.POST['fusername'])
		user_obj=request.user
		#clean this data
		text=request.POST['text']
		friendship=FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj,confirm_request=2,blocked_status=0) |Q(username=fuser_obj,fusername=user_obj,confirm_request=2,blocked_status=0))
		if friendship.exists():
			obj=Message.objects.create(username=request.user,fusername=fuser_obj,text=text)
			#print('done')
			#print(obj)
			content=render_to_string('chat/partials/single_message.html',{'x':obj,'user':request.user},request)
			return JsonResponse(content,safe=False)
		#print('nope')
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
		##print(msg_list.username)
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
				#print(obj)
				return JsonResponse(0,safe=False)
			FriendsWith.objects.create(username=user_obj,fusername=fuser_obj)
			Notification.objects.create(from_user=user_obj,to_user=fuser_obj,notification_type='SR')
		elif type=='Delete' or type=='Unfriend' or type=='Cancel':
			#write code to update te result
			FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj)).delete()
		elif type=='Confirm':
			FriendsWith.objects.filter(Q(username=user_obj,fusername=fuser_obj) |Q(username=fuser_obj,fusername=user_obj)).update(confirm_request=2)
			#print('hey')
			Notification.objects.create(from_user=user_obj,to_user=fuser_obj,notification_type='CR')
			#print('done')
		else:
			#print('hhh')
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
			print('nope')
			print(sid)
			print(type(sid.username))
			print(type(request.user))
			#return
			if request.user is not sid.username:
				print('yes')
				LoggedInUser=get_object_or_404(User,pk=request.user.pk)
				print(LoggedInUser)
				friends_obj=get_object_or_404(User,pk=sid.username.pk)
				print(friends_obj)
				print(sid)
				print(type(sid))
				#Notification.objects.create(from_user=request.user,to_user=friends_obj,sid=sid,notification_type='P')
				if request.user!=friends_obj:
					Notification.objects.create(from_user=request.user, to_user=friends_obj,sid=sid, notification_type='C')
				#Notification.objects.create(from_user=LoggedInUser,to_user_id=sid.username,notification_type='C')
			print('exit')
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
			#return render(request, 'uposts/partials/comments.html',{'comments': comments})
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
		#print('here')
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
		PostNotification=Notification.objects.none()
		for x in chatusers:
			PostNotification=PostNotification|Notification.objects.filter(from_user=x,to_user__isnull=True,is_read=False)
		notifications=((IndividualNotifications|PostNotification)|Notification.objects.filter(to_user=request.user,is_read=False))[:4]
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
		PostNotification=Notification.objects.none()
		for x in chatusers:
			PostNotification=PostNotification|Notification.objects.filter(from_user=x,to_user__isnull=True)

		notifications=(IndividualNotifications|PostNotification|Notification.objects.filter(to_user=request.user,is_read=False)).select_related('from_user')
		return render(request,"notification/notifications.html",{'notifications':notifications})

	return JsonResponse(1,safe=False)


def check_contification(request):
	if request.is_ajax():
		chatusers=Check_user_online(request,request.user)
		IndividualNotifications=Notification.objects.none()
		for x in chatusers:
			IndividualNotifications=IndividualNotifications|Notification.objects.filter(from_user=x,to_user=request.user,is_read=False)
		PostNotification=Notification.objects.none()
		for x in chatusers:
			PostNotification=PostNotification|Notification.objects.filter(from_user=x,to_user__isnull=True,is_read=False)

		notifications=(IndividualNotifications|PostNotification)|Notification.objects.filter(to_user=request.user,is_read=False)
		data=len(notifications)
		return JsonResponse(data,safe=False)


def WhoLikedStatus(request):
	if request.is_ajax():
		id=request.GET.get('id')
		#print(id)
		PersonNames=StatusLikes.objects.filter(sid=Status.objects.get(id=id))
		for x in PersonNames:
			print(x)
		content=render_to_string('uposts/partials/PersonLikedPosts.html',{'PersonLikedPosts':PersonNames},request)
		#print(content)
		return JsonResponse(content,safe=False)

def WhoLikedComment(request):
	if request.is_ajax():
		id=request.GET.get('id')
		#print(id)
		PersonNames=CommentLikes.objects.filter(cid=Comment.objects.get(id=id))
		for x in PersonNames:
			print(x)
		content=render_to_string('uposts/partials/PersonLikedPosts.html',{'PersonLikedPosts':PersonNames},request)
		#print(content)
		return JsonResponse(content,safe=False)

def autocompleteforGroup(request):
	if request.is_ajax():
		search=request.GET.get('val')
		return JsonResponse(0,safe=False)
