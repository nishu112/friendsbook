from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
admin.site.register(Status)
admin.site.register(Profile)
admin.site.register(StatusLikes)
admin.site.register(FriendsWith)
admin.site.register(Message)
admin.site.register(Comment)
admin.site.register(Groups)
admin.site.register(CommentLikes)
admin.site.register(ConsistOf)
admin.site.register(GroupContainsStatus)

#admin.site.register(Gender)

#admin.site.register(Education)

#class ProfileInline(admin.StackedInline):
#    model=Profile
#    can_delete=False
#    verbose_name_plural='Profile'
#
##define a new admin
#class UserAdmin(BaseUserAdmin):
#    inlines=(ProfileInline,)

#re-register UserAdmin
#admin.site.unregister(User)
#admin.site.register(User,UserAdmin)
