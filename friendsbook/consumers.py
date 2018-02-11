import json
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from channels.sessions import channel_session
from friendsbook.models import Message,LoggedInUser,Profile
from django.contrib.auth.models import User
import getpass

@channel_session_user_from_http
def ws_connect(message):
    #print("connected")
    LoggedInUser.objects.get_or_create(user=User.objects.get(username=message.user.username))
    data=LoggedInUser.objects.all()
    Group('users').add(message.reply_channel)
    Group(message.user.username).add(message.reply_channel)
    message.reply_channel.send({"accept": True})
    profile_obj=Profile.objects.get(username=User.objects.get(username=message.user.username))
    fname=profile_obj.fname
    lname=profile_obj.lname
    Group('users').send({
    'text':json.dumps({
    'type':'online',
    'user':message.user.username,
    'fname':fname,
    'lname':lname,
    'is_logged_in':True
    })
    })

@channel_session_user_from_http
def ws_receive(message):
    val=json.loads(message.content['text'])
    user=val['user']
    fuser=val['fuser']
    text=val['text']
    user_obj=User.objects.get(username=user)
    fuser_obj=User.objects.get(username=fuser)
    obj=Message.objects.create(username=user_obj,fusername=fuser_obj,text=text)
    Group(user).send({
        'text': json.dumps({
            'type':'message',
            'text':text,
            'user':user,
            'fuser':fuser,
            'time':str(obj.time)
        })
    })
    Group(fuser).send({
        'text': json.dumps({
            'type':'message',
            'text':text,
            'user':user,
            'fuser':user,
            'time':str(obj.time)
        })
    })


@channel_session_user
def ws_disconnect(message):
    LoggedInUser.objects.filter(user=User.objects.get(username=message.user.username)).delete()
    profile_obj=Profile.objects.get(username=User.objects.get(username=message.user.username))
    fname=profile_obj.fname
    lname=profile_obj.lname
    Group('users').send({
    'text':json.dumps({
    'type':'online',
    'user':message.user.username,
    'fname':fname,
    'lname':lname,
    'is_logged_in':False
    })
    })
    Group('users').discard(message.reply_channel)
    Group(message.user.username).discard(message.reply_channel)
