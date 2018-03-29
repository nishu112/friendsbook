from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.urls import path,include
from django.conf.urls import url
from django.shortcuts import HttpResponse
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path(r'login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.RegistrationView.as_view(), name='signup'),
    path('',login_required(views.home),name='index'),
    #path('secret_place/',views.index,name='index1'),
    #going to comment this post url because post list must come in
    url(r'^post/$', login_required(views.home), name='post'),
    url(r'^post/create_post/$',login_required(views.create_post),name='new_post'),
    url(r'^post/(?P<slug>[\w+-]+)/$', login_required(views.PostDetailView), name='postdetail'),
	path('findfriends/', login_required(views.FriendsView.as_view()), name='profiles'),
    url(r'^users/profile/(?P<slug>[\w.@+-]+)/$', login_required(views.UserProfile), name='profile_info'),
    url(r'^users/profile/(?P<slug>[\w.@+-]+)/timeline$', login_required(views.UserProfile), name='profileTimeline'),
    url(r'^users/profile/(?P<slug>[\w.@+-]+)/friends$', login_required(views.UserFriendsList), name='profileFriends'),
    url(r'^users/profile/(?P<slug>[\w.@+-]+)/photos$', login_required(views.UserPhotos), name='UserPhotos'),
    url(r'^users/profile/(?P<slug>[\w.@+-]+)/ChaneProfileInfo$', login_required(views.UserProfileEdit), name='UserProfileEdit'),
    url(r'^users/profile/(?P<slug>[\w.@+-]+)/ChangePassword$', login_required(views.UserChangePassword), name='UserChangePassword'),

    path('ajax/AddFriend/', login_required(views.AddFriend), name='add_friend'),
    path('query/', views.query, name='query'),
    url(r'^ajax/validate_username/$', views.validate_username, name='validate_username'),
    url(r'^ajax/liveSearch/$', login_required(views.liveSearch), name='liveSearch'),
    url(r'^ajax/like_post/$', login_required(views.like), name='post_like'),
    url(r'^ajax/messages/$', login_required(views.user_messages), name='user_messages'),
    url(r'^ajax/loadcomment/$', login_required(views.Comments), name='loadcomment'),
    url(r'^ajax/editcomment/$', login_required(views.EditComments), name='Editcomment'),
    url(r'^ajax/deleteCommentPost/$', login_required(views.deleteCommentPost), name='deleteCommentPost'),
	url(r'^ajax/UpdateProfile/$',login_required(views.UploadProfile.as_view()),name='UpdateProfile'),
    url(r'^ajax/UpdateCover/$',login_required(views.UploadCover.as_view()),name='UpdateCover'),
    url(r'^ajax/groupUpdateCover/$',login_required(views.UploadGroupCover),name='groupUpdateCover'),
    url(r'^ajax/CreateGroup/$', login_required(views.NewGroup), name='NewGroup'),
    url(r'^ajax/feeds/load/', login_required(views.GetUserPostsByAjax), name='LoadPostForTimeline'),
    url(r'^chat-room/$', login_required(views.user_list), name='user_list'),
    url(r'^chat-room/(?P<slug1>[\w.@+-]+)__Messages__(?P<slug2>[\w.@+-]+)/$', login_required(views.Messenger_Chatting), name='Messenger'),
    url(r'^groups/(?P<pk>\d+)/$', login_required(views.grouphome), name='GroupsHomepage'),
    url(r'^groups/(?P<pk>\d+)/about/$', login_required(views.AboutGroup), name='AboutGroup'),
    url(r'^groups/(?P<pk>\d+)/discussion/$', login_required(views.grouphome), name='GroupDiscussion'),
    url(r'^groups/(?P<pk>\d+)/members/$', login_required(views.groupMembers), name='groupMembers'),
    url(r'^groups/(?P<pk>\d+)/videos/$', login_required(views.groupVideos), name='GroupVideos'),
    url(r'^groups/(?P<pk>\d+)/photos/$', login_required(views.GroupsPhotos), name='GroupsPhotos'),
    url(r'^groups/(?P<pk>\d+)/files/$', login_required(views.Groupfiles), name='GroupsFiles'),
    url(r'^groups/(?P<pk>\d+)/manage/$', login_required(views.ManageGroupMember), name='GroupManage'),
    url(r'^groups/(?P<pk>\d+)/EditAboutGroup/$', login_required(views.EditAboutGroupInfo), name='EditAboutGroup'),
    url(r'^groups/(?P<pk>\d+)/settings/$', login_required(views.GroupsSettings), name='Groupsettings'),
    url(r'^ajax/groups/autocomplete/$', login_required(views.autocompleteforGroup), name='autocomplete'),
    url(r'^ajax/groups/joinrequest$', login_required(views.joinrequest), name='joinrequest'),
    url(r'^ajax/groups/Leave$', login_required(views.LeaveGroup), name='LeaveGroup'),
    url(r'^ajax/groups/addnewMembertoGroup/$', login_required(views.AddMembers), name='addgroupmember'),
    url(r'^ajax/groups/AdminAddQueueMembers/$', login_required(views.AdminAddQueueMembers), name='AdminAddQueueMembers'),
    url(r'^ajax/groups/GroupMemberListActions/$', login_required(views.MemberListActions), name='GroupMemberListActions'),
    url(r'^ajax/SendMessages/$', login_required(views.Message_received), name='Message_received'),
    url(r'^ajax/SeeLikedPostsUsers/$', login_required(views.WhoLikedStatus), name='StatusLikesNames'),
    url(r'^ajax/SeeLikedCommentUsers/$', login_required(views.WhoLikedComment), name='SeeLikedCommentUsers'),
    url(r'^ajax/getPostsForModal/$', login_required(views.getSinglePost), name='getSinglePost'),
    url(r'^notifications/$', login_required(views.get_contifications), name='notifications'),
    url(r'^notifications/check/$', login_required(views.check_contification), name='check_notification'),
    url(r'^groups/$', login_required(views.grouphome), name='GroupsHome'),
    #validate_username
]
## learn redirection so that you don't have to use login_required every time
