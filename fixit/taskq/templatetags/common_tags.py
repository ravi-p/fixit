import os
import sys
import math
from os.path import join, abspath, sep, basename
from datetime import datetime
from django import template
from django.conf import settings
from datetime import datetime, timedelta
from  taskq.models import TaskQ
from django.utils.timesince import timesince
from django.contrib.auth.models import User
from django.core import urlresolvers

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
register = template.Library()


@register.inclusion_tag("show_admin_user.html", takes_context = True)
def show_admin_user(context):
    try:
        request = context['request']
        #perm=request.user.has_perm('taskq.add_task')
        #perm = 'taskq.add_taskq' in request.user.get_all_permissions()
    except Exception, msg:
        request = None
        pass
    is_admin = False
    username = ""
    try:
        if request.user.is_superuser or request.user.is_staff:
            is_admin = True
            username = request.user.username
        else:
            username = request.user.first_name
    except Exception, msg:
        pass
    return {'is_admin': is_admin, 'username' : username, 'is_auth':\
            request.user.is_authenticated}




@register.simple_tag
def namespace_url(namespace, view_name,args=None):
    if not args:
        app_url = urlresolvers.reverse('%s:%s' % (namespace, view_name))
    else:
        app_url = urlresolvers.reverse('%s:%s' % (namespace, view_name),args=[args])
        
    return app_url 



@register.simple_tag
def time_required(task_id):
    task = TaskQ.objects.get(id=task_id)
    if task.repeatable:
        open_time = task.repeat_time
    else:
        open_time = task.created
    close_time = task.completed

    try:
        delta = close_time - open_time
    except:
        return "NA"
    deltaMinutes      = delta.seconds // 60
    deltaHours        = delta.seconds // 3600
    deltaMinutes     -= deltaHours * 60
    deltaWeeks        = delta.days    // 7
    deltaSeconds      = delta.seconds - deltaMinutes * 60 - deltaHours * 3600
    deltaDays         = delta.days    - deltaWeeks * 7
    time_req = ""
    if deltaWeeks:
        time_req += "%sw "%deltaWeeks
    if deltaDays:
        time_req += "%sd "%deltaDays
    if deltaHours:
        time_req += "%sh "%deltaHours
    if deltaMinutes:
        time_req += "%sm "%deltaMinutes
    if deltaSeconds and not time_req:
        time_req += "1 minute"
    return time_req


# get timesince value of pending task. (normal task)
@register.simple_tag
def pending_timesince(task_id):
    task = TaskQ.objects.get(id=task_id)
    open_time = task.created
    cur_time = datetime.now()
    try:
        delta = cur_time - open_time
    except:
        return "NA"

    # Do not show negative time.
    if delta.days < 0:
        return "NA"

    deltaMinutes      = delta.seconds // 60
    deltaHours        = delta.seconds // 3600
    deltaMinutes     -= deltaHours * 60
    deltaWeeks        = delta.days    // 7
    deltaSeconds      = delta.seconds - deltaMinutes * 60 - deltaHours * 3600
    deltaDays         = delta.days    - deltaWeeks * 7
    time_req = ""
    if deltaWeeks:
        time_req += "%sw "%deltaWeeks
    if deltaDays:
        time_req += "%sd "%deltaDays
    if deltaHours:
        time_req += "%sh "%deltaHours
    if deltaMinutes:
        time_req += "%sm "%deltaMinutes
    if deltaSeconds and not time_req:
        time_req += "1 minute"

    if not time_req:
        return "1 minute"
    return time_req


# get timesince value of pending task. (repeatable task)
@register.simple_tag
def repeat_timesince(task_id):
    task = TaskQ.objects.get(id=task_id)
    open_time = task.repeat_time
    #open_time = open_time.replace(hour=0, minute=0, second=0)
    cur_time = datetime.now()
    try:
        delta = cur_time - open_time
    except:
        return "NA"

    # Do not show negative time.
    if delta.days < 0:
        return "NA"

    deltaMinutes      = delta.seconds // 60
    deltaHours        = delta.seconds // 3600
    deltaMinutes     -= deltaHours * 60
    deltaWeeks        = delta.days    // 7
    deltaSeconds      = delta.seconds - deltaMinutes * 60 - deltaHours * 3600
    deltaDays         = delta.days    - deltaWeeks * 7
    time_req = ""
    if deltaWeeks:
        time_req += "%sw "%deltaWeeks
    if deltaDays:
        time_req += "%sd "%deltaDays
    if deltaHours:
        time_req += "%sh "%deltaHours
    if deltaMinutes:
        time_req += "%sm "%deltaMinutes
    if deltaSeconds and not time_req:
        time_req += "1 minute"
    return time_req


@register.simple_tag
def show_task_desc(task_id):
    task = TaskQ.objects.get(id=task_id)
    return task.desc


@register.inclusion_tag("show_pending_cnt.html", takes_context = True)
def show_pending_cnt(context):
    try:
        request = context['request']
    except Exception, msg:
        request = None
    namespace = request.resolver_match.namespace
    tasks = TaskQ.objects.filter(app=namespace,status__in=['P', 'I'])
    if request:
        if not request.user.is_superuser:
            tasks = tasks.exclude(repeat_time__gt=datetime.now())
    return { 'task_cnt': len(tasks) }


@register.inclusion_tag("show_pending_cnt.html", takes_context = True)
def show_complete_cnt(context):
    try:
        request = context['request']
    except Exception, msg:
        request = None
    namespace = request.resolver_match.namespace
    tasks = TaskQ.objects.filter(app=namespace,status='C')
    return { 'task_cnt': len(tasks) }


@register.inclusion_tag("show_pending_cnt.html", takes_context = True)
def show_other_cnt(context):
    try:
        request = context['request']
    except Exception, msg:
        request = None
    namespace = request.resolver_match.namespace
    x_tasks = TaskQ.objects.filter(app=namespace,status='X')
    return { 'task_cnt': len(x_tasks) }


@register.simple_tag
def show_location(task):
    location = ""
    location += task.get_floor_display() + " => "
    location += task.get_room_display()
    return location


@register.simple_tag
def show_priority(task):
    priority = ""
    if task.priority == '1':
        priority="Blocker"
    elif task.priority == '2':
        priority="High"
    elif task.priority == '3':
        priority="Moderate"
    elif task.priority == '4':
        priority="Low"
    else:
        priority="Suggestion"
    return priority


@register.simple_tag
def show_pending_priority(task):
    priority = ""
    if task.priority == '1':
        priority="<span class='bg-blocker'>Blocker</span>"
    elif task.priority == '2':
        priority="<span class='bg-high'>High</span>"
    elif task.priority == '3':
        priority="<span class='bg-moderate'>Moderate</span>"
    elif task.priority == '4':
        priority="<span class='bg-low'>Low</span>"
    else:
        priority="<span class='bg-low'>Suggestion</span>"
    return priority


@register.simple_tag
def get_task_cuser(task):
    user = ''
    try:
        user = User.objects.get(id=task.cuser)
        if user:
            return user.username
    except Exception, msg:
        print msg
    return "NA"


@register.simple_tag
def get_task_euser(task):
    user = ''
    try:
        user = User.objects.get(id=task.euser)
        if user:
            return user.username
    except Exception, msg:
        print msg
    return "NA"
    


