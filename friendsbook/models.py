from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from slugify import slugify
from django.core.validators import RegexValidator
from django.utils.html import escape
# Create your models here.

class UserManager(models.Manager):
    def unatural_key(self):
        return self.username
    User.natural_key = unatural_key

class LoggedInUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,on_delete='CASCADE', related_name='logged_in_user')


class Status(models.Model):
    FriendsOfFriends = 'fsofs'
    PUBLIC= 'Pbc'
    Friends='fs'
    OnlyMe='me'
    PRIVACY_CHOICES = (
        (FriendsOfFriends, 'Friends Of Friends'),
        (PUBLIC ,'Public'),
        (Friends ,'Friends'),
        (OnlyMe ,'OnlyMe'),
    )
    privacy = models.CharField(
        max_length=5,
        choices=PRIVACY_CHOICES,
         null=True,blank=True
    )

    title=models.CharField(max_length=30,default="updated status",null=True)
    username = models.ForeignKey(User,on_delete=models.CASCADE,related_name='fbuser')
    text = models.TextField(blank=True, null=True)
    gid=models.ForeignKey('Groups',on_delete=models.CASCADE,related_name='group_posts',null=True)
    image = models.FileField(upload_to="media/image",null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(null=False,unique=True,blank=False)
    likes=models.IntegerField(default=0)

    class Meta:
        #unique_together = (('username', 'dp'),)
        #managed = False
        db_table = 'status'
        verbose_name_plural = "Status"

    def save(self):
        super(Status, self).save()
        self.slug = 'posts-%s-%i' % (
        self.username,self.id)
        super(Status, self).save()

    def __str__(self):
        return self.slug

class Profile(models.Model):

    username=models.OneToOneField(User,on_delete=models.CASCADE)
    fname = models.CharField( max_length=20,blank=False,null=False)  # Field name made lowercase.
    lname = models.CharField(max_length=20, blank=True, null=True)
    emailid = models.EmailField(max_length=30)
    # Field name made lowercase.
    country_code = models.IntegerField(blank=True, null=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_no = models.CharField(validators=[phone_regex], max_length=17, blank=True,null=True) # validators should be a list

    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=6)
    city = models.CharField(max_length=30, blank=True, null=True)
    state = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)
    slug = models.SlugField(null=False,unique=True,blank=False)
    sid=models.ForeignKey(Status,on_delete=models.SET_NULL,null=True,blank=True)#for image
    profileCover=models.ForeignKey(Status,on_delete=models.SET_NULL,null=True,blank=True,related_name='profileCover')


    class Meta:
        #managed = False
        db_table = 'user'
        verbose_name_plural = "Profile"

    def __str__(self):
        return self.slug

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(username=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def save(self, force_insert=False, force_update=False, using=None):
        super(Profile, self).save()
        self.slug = '%s-%s' % (
        self.username,self.fname)
        super(Profile, self).save()

class StatusLikes(models.Model):
    username = models.ForeignKey(User,on_delete=models.CASCADE)
    sid      = models.ForeignKey(Status,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'status_likes'
        verbose_name_plural = "StatusLikes"

class FriendsWith(models.Model):
    username = models.ForeignKey(User,on_delete=models.CASCADE)
    fusername =models.ForeignKey(User,on_delete=models.CASCADE,related_name='fusername')  # Field name made lowercase.
    time = models.DateTimeField(auto_now_add=True)
    confirm_request = models.SmallIntegerField(default=1)
    blocked_status = models.IntegerField(default=0)

    class Meta:
        db_table = 'friends_with'
        verbose_name_plural = "FriendsWith"

class Message(models.Model):
    username = models.ForeignKey(User,on_delete=models.CASCADE)
    fusername =models.ForeignKey(User,on_delete=models.CASCADE,related_name='fchat_username')  # Field name made lowercase.
    text = models.TextField(null=False,blank=False)
    image = models.FileField(upload_to="chat/image",null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    is_read=models.BooleanField(default=False)

    class Meta:
        db_table = 'message'
        verbose_name_plural = "Message"

class Comment(models.Model):
    username = models.ForeignKey(User,on_delete=models.CASCADE)
    image = models.BinaryField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    sid = models.ForeignKey(Status,on_delete=models.CASCADE)
    slug = models.SlugField(null=False,unique=True,blank=False)
    likes=models.IntegerField(default=0)

    class Meta:
        db_table = 'comment'
        verbose_name_plural = "comment"

    def save(self, force_insert=False, force_update=False, using=None):
        super(Comment, self).save()
        self.slug = 'comment-%s-%i' % (
        self.username,self.id)
        super(Comment, self).save()

    def __str__(self):
        return self.slug


class CommentLikes(models.Model):
    username = models.ForeignKey(User,on_delete=models.CASCADE)
    cid = models.ForeignKey(Comment,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comment_like'
        verbose_name_plural = "comment_like"


class Groups(models.Model):
    OPEN = 'OP'
    CLOSED = 'CL'
    PRIVACY_CHOICES = (
        (OPEN, 'OPEN'),
        (CLOSED, 'CLOSED'),
    )
    gname = models.CharField(max_length=20)
    time = models.DateTimeField(auto_now_add=True)
    id = models.AutoField(primary_key=True)
    privacy = models.CharField(
        max_length=2,
        choices=PRIVACY_CHOICES,
        default=CLOSED,
    )
    cover=models.ForeignKey(Status,on_delete=models.SET_NULL,null=True,blank=True)
    about=models.CharField(max_length=150,null=True,blank=True)
    #for group photo

    class Meta:
        db_table='group'
        verbose_name_plural = "group"

class ConsistOf(models.Model):
    username = models.ForeignKey(User,on_delete=models.CASCADE,related_name='groupuser')
    gid =models.ForeignKey(Groups,on_delete=models.CASCADE,related_name='groupid')
    gadmin = models.SmallIntegerField(default=0)
    confirm = models.SmallIntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'consist_of'
        verbose_name_plural = "consist_of"
        unique_together = ("gid", "username")


class Notification(models.Model):
    POSTED = 'P'
    LIKED = 'L'
    COMMENTED = 'C'
    COMMENTED_LIKE = 'CL'
    EDITED_POST = 'E'
    ALSO_COMMENTED = 'S'
    SEND_REQUEST = 'SR'
    CONFIRM_REQUEST = 'CR'
    POSTED_GROUP = 'PG'
    NOTIFICATION_TYPES = (
        (POSTED, 'Posted'),
        (LIKED, 'Liked'),
        (COMMENTED, 'Commented'),
        (COMMENTED_LIKE, 'Comment Like'),
        (EDITED_POST, 'Edited Post'),
        (ALSO_COMMENTED, 'Also Commented'),
        (SEND_REQUEST, 'Send Request'),
        (CONFIRM_REQUEST, 'Confirm Request'),
        (POSTED_GROUP ,'Posted in Group')
        )

    _POST_TEMPLATE = '<a href="/users/profile/{0}/">{1}</a> Post an  <a href="/post/{2}/">status</a>'  # noqa: E501
    _LIKED_TEMPLATE = '<a href="/users/profile/{0}/">{1}</a> liked your  <a href="/post/{2}/">post</a>'  # noqa: E501
    _COMMENTED_TEMPLATE = '<a href="/users/profile/{0}/">{1}</a> commented on your  <a href="/post/{2}/">post</a>'  # noqa: E501
    _COMMENTED_LIKE_TEMPLATE = '<a href="/users/profile/{0}/">{1}</a> Liked your  Comment on <a href="/post/{2}/">Post</a>'  # noqa: E501
    _EDITED_POST_TEMPLATE = '<a href="/users/profile/{0}/">{1}</a> edited  <a href="/post/{2}/">Post</a>'  # noqa: E501
    _ALSO_COMMENTED_TEMPLATE = '<a href="/users/profile/{0}/">{1}</a> also commentend on the : <a href="/post/{2}/">Post</a>'  # noqa: E501
    _USER_SEND_REQUEST = '<a href="/users/profile/{0}/">{1}</a> Send a friend request '  # noqa: E501
    _USER_ACCEPTED_REQUEST = '<a href="/users/profile/{0}/">{1}</a> Accepted your friend request '  # noqa: E501
    _USER_GROUP_POST = '<a href="/users/profile/{0}/">{1}</a>Post an Status in <a href="/groups/{2}/">{3}</a> '  # noqa: E501

    from_user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='+')
    to_user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='+')
    date = models.DateTimeField(auto_now_add=True)
    sid = models.ForeignKey(Status,on_delete=models.CASCADE, null=True, blank=True)
    cid = models.ForeignKey(Comment,on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=2,
                                         choices=NOTIFICATION_TYPES)
    gid=models.ForeignKey(Groups,on_delete=models.CASCADE,null=True,blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ('-date',)

    def __str__(self):
        profile=Profile.objects.get(username=self.from_user)
        if self.notification_type == self.LIKED:
            return self._LIKED_TEMPLATE.format(
                escape(profile),
                escape(self.from_user.profile.fname),
                self.sid.slug)
        elif self.notification_type == self.POSTED:
            return self._POST_TEMPLATE.format(
                escape(profile),
                escape(self.from_user.profile.fname),
                self.sid.slug)
        elif self.notification_type == self.COMMENTED_LIKE:
            return self._COMMENTED_LIKE_TEMPLATE.format(
                escape(profile),
                escape(self.from_user.profile.fname),
                self.sid.slug)
        elif self.notification_type == self.COMMENTED:
            return self._COMMENTED_TEMPLATE.format(
                escape(profile),
                escape(self.from_user.profile.fname),
                self.sid.slug)
        elif self.notification_type == self.EDITED_POST:
            return self._EDITED_POST_TEMPLATE.format(
                escape(profile),
                escape(self.from_user.profile.fname),
                self.sid.slug)
        elif self.notification_type == self.ALSO_COMMENTED:
            return self._ALSO_COMMENTED_TEMPLATE.format(
                escape(profile),
                escape(self.from_user.profile.fname),
                self.sid.slug)
        elif self.notification_type == self.SEND_REQUEST:
            return self._USER_SEND_REQUEST.format(
                escape(profile),
                escape(self.from_user.profile.fname))
        elif self.notification_type == self.CONFIRM_REQUEST:
            return self._USER_ACCEPTED_REQUEST.format(
                escape(profile),
                escape(self.from_user.profile.fname))
        elif self.notification_type == self.POSTED_GROUP:
            return self._USER_GROUP_POST.format(
                escape(profile),
                escape(self.from_user.profile.fname),
                self.gid.id,escape(self.gid.gname))
        else:
            return 'Ooops! Something went wrong.'

        class Meta:
            db_table='notification'
            verbose_name_plural = "notification"
