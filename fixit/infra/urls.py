from django.conf.urls import patterns, url
from taskq import views
urlpatterns = patterns( '',
    url(r'^$', views.task_list, name='task_list'),
    url(r'^add/$', views.add_task, name='add_task'),
    url(r'^edit/(?P<task_id>\w+)/$', views.edit_task, name='edit_task'),
    url(r'^done/(?P<task_id>\w+)/$', views.mark_task_complete, \
        name='mark_task_complete'),
    url(r'^pending/(?P<task_id>\w+)/$', views.mark_task_pending, \
        name='mark_task_pending'),
    url(r'^delete/(?P<task_id>\w+)/$', views.delete_task, name='delete_task'),
    url(r'^list/$', views.task_list, name='task_list'),
    url(r'^task/(?P<task_id>\w+)/$', views.task_details, name='task_details'),
    url(r'^clist/$', views.completed_list, name='completed_list'),
    url(r'^other/$', views.other_list, name='other_list'),
    #url(r'^other/$', OtherList.as_view(), name='other_list'),
    url(r'^rtlog/$', views.repeat_task_log, name='repeat_task_log'),
    url(r'^getroom/$', views.get_related_rooms, name='get_related_room'),

)
