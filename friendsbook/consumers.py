import json
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from channels.sessions import channel_session
from friendsbook.models import Message,LoggedInUser,Profile
from django.contrib.auth.models import User
from django.template.loader import render_to_string
import getpass
import time
from .models import *

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
    print(val)
    print('donewhat??')
    type=val['type']
    print('ok')
    print(type)
    user=val['user']
    fuser=val['fuser']
    user_obj=User.objects.get(username=user)
    fuser_obj=User.objects.get(username=fuser)
    if type=='read_messages':
        print('done ')
        #Message.objects.filter(username=fuser_obj,fusername=user_obj,is_read=False).update(is_read=True)
        Group(user).send({
            'text': json.dumps({
                'type':'read_messages',
                'user':str(fuser),
                'fuser':str(user),
            })
        })
        return ;
    if type=='update':
        print(fuser_obj.username)
        print(user_obj.username)
        print('updated')
        print(Message.objects.filter(username=user_obj,fusername=fuser_obj,is_read=False))
        Message.objects.filter(username=fuser_obj,fusername=user_obj,is_read=False).update(is_read=True)
        return ;

    text=val['text']
    print('reached')
    time.sleep(2)
    print('dispatch')
    obj=Message.objects.filter(username=user_obj,fusername=fuser_obj).order_by('-time')[0]
    print(obj)
    print('really')

    content=render_to_string('chat/partials/single_message.html',{'x':obj,'user':fuser})
    Group(user).send({
        'text': json.dumps({
            'type':'message',
            'text':str(obj.text),
            'user':str(obj.username),
            'fuser':str(obj.fusername),
            'time':str(obj.time),
            'content':str(content)
        })
    })
    Group(fuser).send({
        'text': json.dumps({
            'type':'message',
            'text':str(obj.text),
            'user':str(obj.username),
            'fuser':str(obj.username),
            'time':str(obj.time),
            'content':str(content)
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
