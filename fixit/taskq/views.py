# system
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.template import RequestContext, loader
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from itertools import chain
from datetime import datetime, timedelta
from django.views.generic import ListView
import math
from django.core.exceptions import PermissionDenied

#--------------- Logging ------------------
#import logging
#logger = logging.getLogger(__name__)
from fixit import NW_Logger
logger = NW_Logger.get_logger_obj()
def checklog():
    logger.debug("this is a debug message! to check log conf")
 

# custom
from models import TaskQ, save_task, update_task
from models import RepeatTaskLog
from forms import TaskForm, TaskAdminForm,TaskUpdateForm
from django.contrib.auth.models import User,Group
from subprocess import Popen, PIPE
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from taskq.models import ROOM_CHOICES
from taskq.forms import GF,FF,SF,TF,PF,All
from django.views.generic import DetailView


def send_postfix_mail(body, sub, to):
    try:
        cmd = "echo '%s' | mail -s '%s' '%s'"%(body, sub, to)
        sp = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        sp.wait()
        if sp.returncode == 0:
            #logger.info("New task mail sent to admin user.")
            logger.info("mail sent successfully")
        else:
            #print sp.stderr.readlines()
            logger.error("Failed to send postfix mail")

    except Exception, msg:
        logger.error("something went wrong in postfix mail,%s" % str(msg))
        pass


# Create your views here.


    

@csrf_protect
@login_required
def add_task(request):
    """
    GET : Render add task form.
    POST : Validate add task form and save the changes to DB.
    """

    #if not request.user.has_perm('taskq.add_taskq'):
    #    logger.info("permission denied,")
    #    raise PermissionDenied

    template = loader.get_template('add_task.html')
    namespace=request.resolver_match.namespace
    initial_dict={'priority':'4'}

    if request.user.is_superuser or request.user.is_staff or request.user.has_perm('taskq.add_task'):
        initial_dict.update({'app':namespace})
        form = TaskAdminForm(initial=initial_dict)
    else:
        form = TaskForm(initial=initial_dict)

    if request.method == "POST":
        if request.user.is_superuser or request.user.is_staff :
            form = TaskAdminForm(request.POST)
        else:
            form = TaskForm(request.POST)

        if form.is_valid():
            data = {}
            data['floor'] = form.cleaned_data['floor']
            data['room'] = form.cleaned_data['room']
            data['title'] = form.cleaned_data['title']
            data['desc'] = form.cleaned_data['desc']
            data['priority'] = form.cleaned_data['priority']
            data['status'] = 'P'

            if request.POST.has_key('repeatable'):
                repeatable = True
                data['repeat_time'] = form.cleaned_data['repeat_time']
            else:
                repeatable = False
                data['repeat_time'] = None
            data['repeatable'] = repeatable

            if request.user.is_superuser or request.user.is_staff:
                data['app'] = form.cleaned_data['app']
            else:
                data['app'] = namespace


            task = save_task(form_data=data)
            task.cuser = request.user.id

            task.save()

            if repeatable:
                RTL = RepeatTaskLog.objects.create(task_id=task.id,\
                        task_repeat_time=task.repeat_time,
                        status=0, comment="Not Done")
                RTL.save()

            if task:
                success_msg = "Task added successfully."
                messages.add_message(request, messages.SUCCESS, success_msg)
                if task.priority=='1':
                    logger.debug("blocker task has been added .. ")
            else:
                error_msg = "Failed to save task to database."
                logger.error("Failed to save task to database.")
                messages.add_message(request, messages.ERROR, error_msg)

            if namespace=="infra":
                g=Group.objects.get(name="infra")
                email_list=[u.email for u in g.user_set.filter()]
            else:
                g=Group.objects.get(name="housekeeper")
                email_list=[u.email for u in g.user_set.filter()]

            for to in email_list:
                sub = "Fixit:%s New Task @%s-Floor" % (namespace,task.floor)
                #
                # comment out test automated mails.
                #
                desc=task.title + "\n\n" + task.desc
                send_postfix_mail(desc, sub, to)

            #return HttpResponseRedirect(reverse('task_list'))
            namespace=request.resolver_match.namespace
            return HttpResponseRedirect(reverse('%s:%s'%(namespace,'task_list')))
        else:
            task = None
            for err in form.errors.values():
                messages.add_message(request, messages.ERROR, err[0])
    else:
        task = None
    context = RequestContext(request,{
        'task': task, 'form': form,\
        'namespace':request.resolver_match.namespace,\
        'view_name':'add_task',\
        'active': 'addtask'}
        )
    return HttpResponse(template.render(context))


def task_details(request, task_id):
    """
    show task details page.
    """
    if not request.user.has_perm('taskq.view_taskq'):
        logger.error("permission error in task_details view")
        raise PermissionDenied

    template = loader.get_template('task.html')
    task = TaskQ.objects.get(id=task_id)
    heading = ""
    status = ""
    priority = ""

    # Which Floor?
    heading += task.get_floor_display() + " ==> "

    # Which Room?
    heading += task.get_room_display()

    status = task.get_status_display()

    priority = task.get_priority_display()

    context = RequestContext(request, {'task': task, 'heading': heading,\
            'status': status, 'priority': priority})
    return HttpResponse(template.render(context))


@login_required
def edit_task(request, task_id):
    """
    Edit task.
    """
    namespace=request.resolver_match.namespace
    t=TaskQ.objects.get(id=task_id)
    if t.app != namespace:
        # when user changes URL from infra to housekeep or vice versa.
        error_msg = "Permission denied."
        logger.error("permission error in edit task view")
        messages.add_message(request, messages.ERROR, error_msg)
        return HttpResponseRedirect(reverse('%s:%s' % (t.app, 'task_list')))

    if not request.user.is_authenticated:
        error_msg = "Permission denied."
        logger.error("permission error in edit task view")
        messages.add_message(request, messages.ERROR, error_msg)
        return HttpResponseRedirect(reverse('%s:%s' % (namespace, 'task_list')))


    #to only server group field shoud be available
    if namespace == "infra" and request.user.has_perm('taskq.done_task_infra'):
        is_serve=True
    elif namespace == "housekeep" and request.user.has_perm('taskq.done_taskq'):
        is_serve=True
    else: 
        is_serve = False

    template = loader.get_template('edit_task.html')
    task = TaskQ.objects.get(id=task_id)
    task_dict = {
        'floor': task.floor,
        'room': task.room,
        'title': task.title,
        'desc': task.desc,
        'priority': task.priority,
        'repeatable': task.repeatable,
        'repeat_time': task.repeat_time,
        'is_serve':is_serve,
    }

    if request.user.is_staff or request.user.is_superuser or is_serve:
        task_dict.update({'status': task.status,'app':task.app})
        form = TaskAdminForm(initial=task_dict)

    if not request.user.is_staff and not request.user.is_superuser:
        if task.cuser == request.user.id:
            form = TaskForm(initial=task_dict)
        else:
            form = TaskUpdateForm(initial=task_dict)



    if request.method == "POST":
        if request.user.is_staff or request.user.is_superuser or is_serve:
            form = TaskAdminForm(request.POST)
        if not request.user.is_staff and not request.user.is_superuser:
            if task.cuser == request.user.id:
                form = TaskForm(request.POST)
            else:
                form = TaskUpdateForm(request.POST)

        if form.is_valid():
            data = {}
            data['floor'] = form.cleaned_data['floor']
            data['room'] = form.cleaned_data['room']
            data['title'] = form.cleaned_data['title']
            data['desc'] = form.cleaned_data['desc']
            data['priority'] = form.cleaned_data['priority']
                
            if request.user.is_staff or is_serve:
                data['status'] = form.cleaned_data['status']
                data['app'] = form.cleaned_data['app']
            else:
                data['app'] = namespace 


            if request.POST.has_key('repeatable'):
                repeatable = True
                data['repeat_time'] = form.cleaned_data['repeat_time']
            else:
                repeatable = False
                data['repeat_time'] = None

            data['repeatable'] = repeatable

            if request.user.is_staff or is_serve:
                orig_status = task.status
            task = update_task(task, form_data=data)
            if request.user.is_staff or is_serve:
                new_status = task.status

            task.euser = request.user.id
            task.save()
            if task.priority=='1':
                logger.debug('Task updated to blocker priority')

            if request.user.is_staff or is_serve:
                status_change = ""
                if orig_status == "C" and new_status=="P":
                    task.status = 'P'
                    task.completed = None
                    task.save()
                    status_change = "CtoP"

                if orig_status == "P" and new_status=="C":
                    ctime = datetime.now()
                    task.completed = ctime
                    task.status = 'C'
                    task.save()
                    status_change = "PtoC"

                ####################
                if task.repeatable:
                    RTL , created = RepeatTaskLog.objects.get_or_create(task_id=task.id,\
                        task_repeat_time=task.repeat_time)
                    if created:
                        RTL.comment = "Pending"
                        RTL.status = 0
                        RTL.save()
                    else:
                        if status_change == "CtoP":
                            RTL.comment = "Not Done"
                            RTL.status = 0
                            RTL.save()
                        elif status_change == "PtoC":
                            RTL.comment = "Complete"
                            RTL.status = 1
                            RTL.save()
               ####################
            success_msg = "Task updated successfully."
            messages.add_message(request, messages.SUCCESS, success_msg)
            namespace=request.resolver_match.namespace
            return HttpResponseRedirect(reverse('%s:%s' % (namespace, 'task_list')))
        else:
            for err in form.errors.values():
                messages.add_message(request, messages.ERROR, err[0])
            namespace=request.resolver_match.namespace
            return HttpResponseRedirect(reverse('%s:%s' % (namespace, 'edit_task'),args=[task.id]))
    context = RequestContext(request, {\
        'form': form,\
        'namespace':request.resolver_match.namespace,\
        'view_name': 'edit_task',\
        'is_serve':is_serve,\
        })
    return HttpResponse(template.render(context))



def mark_task_complete(request, task_id):
    """
    Logic to mark the task as complete.
    """
    namespace=request.resolver_match.namespace
    if namespace == "infra": 
        if 'task.done_task_infra' not in request.user.get_all_permissions():
            logger.error("permission error while infra done task ")
            raise PermissionDenied

    if namespace == "housekeep": 
        if 'taskq.done_taskq' not in request.user.get_all_permissions():
            logger.error("permission error while housekeep done task ")
            raise PermissionDenied

    task = TaskQ.objects.get(id=task_id)
    ctime = datetime.now()
    task.completed = ctime
    task.status = 'C'
    task.save()

    try:
        if task.repeatable:
            RTL, created = RepeatTaskLog.objects.get_or_create(task_id=task.id,\
                task_repeat_time=task.repeat_time, status=1,comment="complete")
            RTL.save()
    except Exception, msg:
        raise
    if not task.repeatable:
        try:
            uid=task.cuser
            if uid:
                u=User.objects.get(id=uid)
                to=u.email
                if task.title:
                    bdy = "Fixit task titled '%s' has been marked as done."%task.title
                else:
                    bdy = "Fixit task '%s' has been marked as done."%task.desc
                sub="Fixit task done" 
                send_postfix_mail(bdy, sub, to)
        except Exception,e :
            logger.error("send mail errr %s" % str(e) )   


    success_msg = "Task marked as complete."
    messages.add_message(request, messages.SUCCESS, success_msg)
    return HttpResponseRedirect(reverse('%s:%s' % (namespace, 'task_list')))


def mark_task_pending(request, task_id):
    """
    Logic to mark task as incomplete.
    """
        

    namespace=request.resolver_match.namespace
    task = TaskQ.objects.get(id=task_id)
    task.status = 'P'
    task.completed = None
    task.save()
    try:
        if task.repeatable:
            RTL, created = RepeatTaskLog.objects.get_or_create(task_id=task.id,\
                task_repeat_time=task.repeat_time)
            if created:
                RTL.status=1
            else:      
                RTL.status=0
            RTL.comment = "Not Done"
            RTL.save()

    except Exception, msg:
        logging.error("failed to mark as pending, %s" % str(msg))
    success_msg = "Task marked as pending."
    messages.add_message(request, messages.SUCCESS, success_msg)
    return HttpResponseRedirect(reverse('%s:%s' % (namespace, 'task_list')))


def delete_task(request, task_id):
    """
    Delete the task.
    Only superuser can delete the task.
    """
    if 'task.delete_task' in request.user.get_all_permissions():
        TaskQ.objects.get(id=task_id).delete()
        success_msg = "Task deleted successfully."
        messages.add_message(request, messages.SUCCESS, success_msg)
        namespace=request.resolver_match.namespace
        return HttpResponseRedirect(reverse('%s:%s' % (namespace, 'task_list')))
    else:
        error_msg = "Permission Error."
        logging.error("Delete Permission Error")
        messages.add_message(request, messages.error, error_msg)
        namespace=request.resolver_match.namespace
        return HttpResponseRedirect(reverse('%s:%s' % (namespace, 'task_list')))
        #return HttpResponse(template.render(context))


def repeat_task_log(request):
    """
    Show repeat task logs in tabular and modular format.
    Only superuser can access this page.
    """
    if request.user.is_superuser or request.user.is_staff:
        template = loader.get_template('repeat_task_log.html')
        context = RequestContext(request, {})
        RTL = RepeatTaskLog.objects.all()
        rtlog_dict = {}
        rtasks = TaskQ.objects.filter(repeatable=1)
        for rt in rtasks:
            rtl_list =RepeatTaskLog.objects.filter(\
                    task_id=rt.id).order_by('task_repeat_time')
            if not rtl_list:
                continue
            pass_cnt = len(rtl_list.filter(status=1))
            total_cnt = len(rtl_list)
            rtlog_dict.update({'%s'%rt.id: {'rtl_list': rtl_list, \
                    'pass_cnt': pass_cnt, 'total_cnt':total_cnt}})

        context = RequestContext(request, 
            {
                'RTL': RTL, 'rtasks':rtasks,\
                'rtlog_dict': rtlog_dict,\
                'active': 'rtlog',\
                'namespace':request.resolver_match.namespace
            })
        return HttpResponse(template.render(context))
    else:
        error_msg = "Access denied."
        messages.add_message(request, messages.error, error_msg)
        namespace=request.resolver_match.namespace
        return HttpResponseRedirect(reverse('%s:%s' % (namespace, 'task_list')))
        #return HttpResponse(template.render(context))



def task_list(request):
    """
    List of all pending tasks.
    This is main landing page. Home page.
    """

    template = loader.get_template('task_list.html')
    namespace = request.resolver_match.namespace
    p_tasks = TaskQ.objects.filter(app=namespace)
    col_nm =  request.GET.get('sort_by',"priority")
    s_order=  request.GET.get('order',"ASC")
    if col_nm=="location":
        if s_order=='ASC':
            p_tasks = p_tasks.filter().order_by('floor', 'priority')
        if s_order=='DESC':
            p_tasks = p_tasks.filter().order_by('-floor', 'priority')

    else:
        i_tasks = n_tasks = c_tasks = []
        #tasks = TaskQ.objects.all()
        #tasks = tasks.order_by('priority')
        tasks = p_tasks.order_by('priority')
        p_tasks = tasks.filter(status='P')
        progress = tasks.filter(status='I')
        if not request.user.is_superuser:
            p_tasks = p_tasks.exclude(repeat_time__gt=datetime.now())

        p_tasks = list(chain(progress, p_tasks))

    if request.is_ajax():
        try:
            Fpg=request.session.get('Fpg')
            Bpg=request.session.get('Bpg')
            p = Paginator(p_tasks, 5)
            if request.GET['direction']=='forword':
                if p.page(Fpg - 1).has_next():
                    p_tasks = p.page(Fpg)
                    Fpg+=1
                    Bpg+=1
                    request.session['Fpg'] = Fpg
                    request.session['Bpg'] = Bpg
                else:
                    return HttpResponseNotFound("forword")
            elif request.GET['direction']=='backword':
                if p.page(Bpg).has_previous():
                    Bpg-=1
                    p_tasks = p.page(Bpg)
                    Fpg-=1
                    request.session['Fpg'] = Fpg
                    request.session['Bpg'] = Bpg
                else:
                    return HttpResponseNotFound("backword")

            else:
                pass
        except Exception,e:
            logging.error("failed in task list pagination, %s" % str(msg))
            

        return render_to_response('task_list_table_row.html',{
                "p_tasks": p_tasks.object_list,
                "request":request,
                "namespace":namespace
                })

    p_tasks=p_tasks[0:20]
    context = RequestContext(request, {
                'p_tasks': p_tasks,\
                'sort_by': col_nm,\
                's_order': s_order,\
                'namespace': namespace,\
                'view_name': 'task_list',\
                'active': 'tasklist',})

    request.session['Fpg'] = 5
    request.session['Bpg'] = 1
    return HttpResponse(template.render(context))

def completed_list(request):
    """
    List of all completed tasks.
    """
    template = loader.get_template('completed_list.html')
    p_tasks =  i_tasks = n_tasks = c_tasks = []
    namespace = request.resolver_match.namespace
    tasks = TaskQ.objects.filter(app=namespace)
    #tasks = TaskQ.objects.all()

    tasks = tasks.order_by('priority')
    p_tasks = tasks.filter(status='P')
    c_tasks = tasks.filter(status='C')
    i_tasks = tasks.filter(status='I')
    n_tasks = tasks.filter(status='N')

    pending_cnt = len(p_tasks)
    complete_cnt = len(c_tasks)
    progress_cnt = len(i_tasks)
    impossible_cnt = len(n_tasks)
    other_cnt = progress_cnt + impossible_cnt


    #
    # Complete tasks
    #
    c_tasks = tasks.filter(status='C').order_by('-completed')

    task_cnt = len(tasks)
    complete_cnt = len(c_tasks)

    now = datetime.now()
    last_week = now - timedelta(days=7)
    week_tasks =  tasks.filter(created__range=[last_week, now]).exclude(\
            status='I')
    week_cnt = len(week_tasks)
    week_done_cnt = len(week_tasks.filter(status='C'))

    if len(week_tasks.filter(status='C')):
        #avg_closure_time = float(len(week_tasks)) /\
        #    len(week_tasks.filter(status='C'))
        #avg_closure_time = int(math.ceil(avg_closure_time))
        task_done_rate = round(float(len(week_tasks.filter(status='C'))) * 100 / \
                len(week_tasks), 2)
        task_done_rate = "%s %%"%task_done_rate

    else:
        if len(week_tasks.filter(status='P')):
            #avg_closure_time = 0
            task_done_rate = "0%"
        else:
            #avg_closure_time = "NA"
            task_done_rate = "NA"

    if request.is_ajax():
        try:
            Fpg=request.session.get('Fpg')
            Bpg=request.session.get('Bpg')
            p = Paginator(c_tasks, 5)
            if request.GET['direction']=='forword':
                if p.page(Fpg-1).has_next():
                    c_tasks = p.page(Fpg)
                    Fpg+=1
                    Bpg+=1
                    request.session['Fpg'] = Fpg
                    request.session['Bpg'] = Bpg
                else:
                    return HttpResponseNotFound("forword")
            elif request.GET['direction']=='backword':
                if p.page(Bpg).has_previous():
                    Bpg-=1
                    c_tasks = p.page(Bpg)
                    Fpg-=1
                    request.session['Fpg'] = Fpg
                    request.session['Bpg'] = Bpg
                else:
                    return HttpResponseNotFound("backword")

            else:
                pass
        except Exception,e:
            logging.error("failed in complete_list pagination, %s" % str(msg))
        return render(request, 'completed_list_table_row.html',{
            "c_tasks": c_tasks,\
            "namespace":namespace,\
            "view_name":"completed_list",\
        })


    c_tasks=c_tasks[0:20]
    context = RequestContext(request, {
                'tasks':tasks,\
                'c_tasks': c_tasks,
               # 'ctask_list':ctask_list, \
                'task_cnt': task_cnt, 'pending_cnt': pending_cnt,\
                'complete_cnt': complete_cnt, 'progress_cnt':progress_cnt,\
                #'avg_closure_time': avg_closure_time,
                'week_cnt': week_cnt,\
                'week_done_cnt': week_done_cnt,\
                'task_done_rate': task_done_rate,\
                'active': 'ctasklist',\
               # 'target':'/task/clist/'\
                "namespace":namespace,\
                "view_name":"completed_list",\
                })
    request.session['Fpg'] = 5
    request.session['Bpg'] = 1
    return HttpResponse(template.render(context))




def other_list(request):

    """
    List of tasks marked as incomplete.
    """

    template = loader.get_template('other_list.html')
    namespace = request.resolver_match.namespace
    tasks = TaskQ.objects.filter(app=namespace)
    col_nm =  request.GET.get('sort_by',"priority")
    s_order=  request.GET.get('order',"ASC")
    if col_nm=="location":
        if s_order=='ASC':
            other_tasks=tasks.order_by('floor','priority')
        if s_order=='DESC':
            other_tasks=tasks.order_by('-floor','priority')
    else:
        tasks = tasks.order_by('priority')
        #
        # Complete tasks
        #
        other_tasks =  tasks.filter(status__in=['X'])
        other_tasks = other_tasks.order_by('modified')
    if request.is_ajax():
        try:
            Fpg=request.session.get('Fpg')
            Bpg=request.session.get('Bpg')
            p=Paginator(other_tasks,5)
            if request.GET['direction']=='forword':
                if p.page(Fpg-1).has_next():
                    other_tasks=p.page(Fpg)
                    Fpg+=1
                    Bpg+=1
                    request.session['Fpg']=Fpg
                    request.session['Bpg']=Bpg
                else:
                    return HttpResponseNotFound('forword')
            elif request.GET['direction']=='backword':
                if p.page(Bpg).has_previous() and Bpg > 0:
                    Fpg-=1
                    other_tasks=p.page(Bpg)
                    Bpg-=1
                    request.session['Fpg']=Fpg
                    request.session['Bpg']=Bpg
                else:
                    return HttpResponseNotFound('backword')
            else:
                pass
        except Exception,e:
            logging.error("failed in other_list pagination, %s" % str(msg))

        return render(request, 'other_list_table_row.html',{
                "xtasks":other_tasks,
                "namespace":namespace,
                "view_name":view_name,
            })

    other_tasks=other_tasks[0:20]
    context = RequestContext(request, {
                'xtasks':other_tasks, \
                'active': 'otherlist',\
                'sort_by': col_nm,\
                's_order': s_order,\
                "namespace":namespace,
                "view_name":"other_list",
                'target':'/task/other/'})

    request.session['Fpg'] = 5
    request.session['Bpg'] = 1
    return HttpResponse(template.render(context))

def task_details_view(request,task_id):
    url = request.build_absolute_uri()
    url=url.rsplit('/',2)[0]

    namespace=request.resolver_match.namespace
    t=TaskQ.objects.get(id=task_id,app=namespace)
    template = loader.get_template('task_details.html')
    try:
        created_by=User.objects.get(id=t.cuser)
    except:
        created_by=""
    context = RequestContext(request,{
            'task': t, \
            'namespace': namespace,\
            'back': url,\
            'created_by':created_by,\
          #  'back': request.session['previous_url'],\
        })
    return HttpResponse(template.render(context))

    
    
    






def get_related_rooms(request):
    # Ajax call to get related rooms 
    if request.is_ajax():
        fl = request.GET.get('id',0)
        res='<option>Select Room (...)</option>'
        if fl=='0':    
            rlist=[i for i in ROOM_CHOICES if i[0] in GF ]
        elif fl=='1':    
            rlist=[i for i in ROOM_CHOICES if i[0] in FF ]
        elif fl=='2':    
            rlist=[i for i in ROOM_CHOICES if i[0] in SF ]
        elif fl=='3':    
            rlist=[i for i in ROOM_CHOICES if i[0] in TF ]
        elif fl=='4':
            if request.resolver_match.namespace == "infra":
                rlist=[('14', 'Battery Room')]   
            else: 
                rlist=[i for i in ROOM_CHOICES if i[0] in PF ]
        elif fl=='5':    
            rlist=[i for i in ROOM_CHOICES if i[0] in All ]
        else:
            rlist=ROOM_CHOICES
        for i in rlist:
            res += "<option value=%s>%s</option>"%(i[0],i[1])
        
        return HttpResponse(res)

