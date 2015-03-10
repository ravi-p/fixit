import os
import django
from fixit import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fixit.settings")
django.setup()
from taskq.models import TaskQ, RepeatTaskLog
from datetime import datetime, timedelta

try:
    tasks = TaskQ.objects.filter(status='P')
    repeat_tasks = tasks.filter(repeatable=True )
    for rt in repeat_tasks:
        if rt.repeat_time > datetime.now():
            # skip
            continue

        try:
            RTL = RepeatTaskLog.objects.get(task_id=rt.id, task_repeat_time=rt.repeat_time)
        except Exception, msg:
            RTL = RepeatTaskLog.objects.create(task_id=rt.id,
                    task_repeat_time=rt.repeat_time, \
                    status='P', comment = None)

        if rt.status == "P":
            RTL.status = 0
            RTL.comment = "Not Done"
            print "Repeatable task marked as INCOMPLETE."
        else:
            RTL.status = 1
            RTL.comment = "Complete"
        RTL.save()

        rt_new_time = None
        now = datetime.now()
        if rt.repeat_time < datetime.now():
            rt_hour = rt.repeat_time.hour
            rt_minute = rt.repeat_time.minute
            rt_second = rt.repeat_time.second

            rt_new_time = rt.repeat_time.replace(year=now.year, \
                    month=now.month, day=now.day, hour=rt_hour, \
                    minute=rt_minute, second=rt_second)

        if not rt_new_time:
            otime = rt.repeat_time
            rt_new_time = otime + timedelta(days=1)

        rt.status = 'P'
        rt.completed = None
        rt.repeat_time = rt_new_time
        rt.save()

except Exception, msg:
    print msg
    pass
