from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from slugify import slugify
# Create your models here.

class UserManager(models.Manager):
    def unatural_key(self):
        return self.username
    User.natural_key = unatural_key

class LoggedInUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,on_delete='CASCADE', related_name='logged_in_user')


class Status(models.Model):
    title=models.CharField(max_length=30,default="updated status",null=True)
    username = models.ForeignKey(User,on_delete=models.CASCADE,related_name='fbuser')
    text = models.TextField(blank=True, null=True)
    gid=models.ForeignKey('Groups',on_delete=models.CASCADE,related_name='group_posts',null=True)
    image = models.FileField(upload_to="media/image",null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    privacy = models.CharField(max_length=5, blank=True, null=True,default="fs")
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
    phone_no = models.BigIntegerField(blank=True, null=True)
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
    text = models.TextField(blank=True, null=True)
    image = models.FileField(upload_to="chat/image",null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)

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
    gname = models.CharField(max_length=20)
    time = models.DateTimeField(auto_now_add=True)
    id = models.AutoField(primary_key=True)
    privacy = models.CharField(max_length=5)
    cover=models.ForeignKey(Status,on_delete=models.SET_NULL,null=True,blank=True)
    #for group photo

    class Meta:
        db_table='group'
        verbose_name_plural = "group"

class ConsistOf(models.Model):
    username = models.ForeignKey(User,on_delete=models.CASCADE,related_name='groupuser')
    gid =models.ForeignKey(Groups,on_delete=models.CASCADE,related_name='groupid')
    gadmin = models.SmallIntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'consist_of'
        verbose_name_plural = "consist_of"
        unique_together = ("gid", "username")

class GroupContainsStatus(models.Model):
    gid=models.ForeignKey(Groups,on_delete=models.CASCADE)
    sid=models.ForeignKey(Status,on_delete=models.CASCADE)
    #for group photo

    class Meta:
        db_table='GroupContainsStatus'
        verbose_name_plural = "GroupContainsStatus"
