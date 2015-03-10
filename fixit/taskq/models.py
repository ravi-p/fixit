from django.db import models

# Create your models here.

FLOOR_CHOICES = (
        ('-1', 'Select Floor (...)'),
        ('0', 'Ground'),
        ('1', 'First'),
        ('2', 'Second'),
        ('3', 'Third'),
        ('4', 'Pantry'),
        ('5', 'All'),
)

ROOM_CHOICES = (
        ('-1', 'Select Room (...)'),
        ('0', 'Conference'),
        ('1', 'Room 1'),
        ('2', 'Room 2'),
        ('3', 'Room 3'),
        ('4', 'WC'),
        ('5', 'Accounts'),
        ('6', 'Server'),
        ('7', 'Lunch Area'),
        ('8', 'Common Passage'),
        ('9', 'Stairwell'),
        ('10', 'Lift'),
        ('11', 'Sink'),
        ('12', 'Barbeque Area'),
        ('13', 'Table Top'),
        ('14', 'Battery Room'),
)

STATUS_CHOICES = (
        ('P', 'Pending'),
        ('I', 'In Progress'),
        ('C', 'Complete'),
        ('X', 'Not Possible'),
)

PRIORITY_CHOICES = (
        ('1', 'Blocker/Critical'),
        ('2', 'High'),
        ('3', 'Moderate'),
        ('4', 'Low'),
        ('5', 'Suggestion/Task'),
)

APP_CHOICES = (
        ('housekeep', 'Housekeeping'),
        ('infra', 'Infrastructure'),
)
class TaskQ(models.Model):
    floor = models.CharField(max_length=255, choices=FLOOR_CHOICES, \
            default='-1')
    room = models.CharField(max_length=255, choices=ROOM_CHOICES,\
            default='-1')
    title = models.CharField(max_length=255)
    desc = models.TextField()
    status = models.CharField(max_length=255, default='P',\
            choices=STATUS_CHOICES)
    priority = models.CharField(max_length=255, null=True, default='4',\
            choices=PRIORITY_CHOICES)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True)
    completed = models.DateTimeField(null=True, blank=True)
    repeatable = models.BooleanField(default=False)
    repeat_time = models.DateTimeField(null=True, blank=True)
    cuser = models.IntegerField(null=True, blank=True)
    euser = models.IntegerField(null=True, blank=True)
    app = models.CharField(max_length=20,default="housekeep",choices=APP_CHOICES)

    class Meta:
        permissions=(
            ('done_taskq','can done taskq'),
            ('done_task_infra','done task infra'),
            ('mark_pend_taskq','can mark as pend taskq'),
            ('view_taskq','can view taskq'),
        )

    def __str__(self):
        return "Task-%s__%s"%(str(self.id), self.desc[:12])

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) \
                for field in self._meta.fields]

def save_task(**kwargs):
    task = None
    try:
        floor = kwargs['form_data']['floor']
        room = kwargs['form_data']['room']
        title = kwargs['form_data']['title']
        desc = kwargs['form_data']['desc']
        priority = kwargs['form_data']['priority']
        repeatable = kwargs['form_data']['repeatable']
        repeat_time = kwargs['form_data']['repeat_time']
        app = kwargs['form_data']['app']
        task = TaskQ.objects.create(floor=floor, room=room, title=title,desc=desc, \
                repeatable=repeatable, repeat_time=repeat_time, app = app,\
                priority=priority)
    except Exception, msg:
        raise
    return task


def update_task(instance=None, **kwargs):
    task = TaskQ.objects.get(id=int(instance.id))
    try:
        orig_repeat_time = task.repeat_time

        floor = kwargs['form_data']['floor']
        room = kwargs['form_data']['room']
        title = kwargs['form_data']['title']
        desc = kwargs['form_data']['desc']
        priority = kwargs['form_data']['priority']
        if kwargs['form_data'].has_key('status'):
            status = kwargs['form_data']['status']
            task.status = status
        repeatable = kwargs['form_data']['repeatable']
        repeat_time = kwargs['form_data']['repeat_time']
        app = kwargs['form_data']['app']
        task.floor = floor
        task.room = room
        task.title = title
        task.desc = desc
        task.repeatable = repeatable
        task.repeat_time = repeat_time
        task.priority = priority
        task.app = app
        task.save()

        try:
            if task.repeatable:
                if task.repeat_time != orig_repeat_time:
                    RTL = RepeatTaskLog.objects.create(task_id=task.id,\
                        task_repeat_time=task.repeat_time,
                        status=0, comment="Not Done")
                else:
                    if task.status == "C":
                        RTL = RepeatTaskLog.objects.get(task_id=task.id,\
                            task_repeat_time=task.repeat_time)
                        RTL.status = 1
                        RTL.comment ="Complete"
                        RTL.save()
        except Exception, msg:
            #print msg
            pass

    except Exception,msg:
        raise
    return task


class RepeatTaskLog(models.Model):
    task_id = models.IntegerField()
    task_repeat_time = models.DateTimeField()
    status = models.BooleanField(default=False)
    comment = models.CharField(max_length=155, null=True)

    def __str__(self):
        return "Repeat_Task-%s"%str(self.task_id)

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) \
                for field in self._meta.fields]




