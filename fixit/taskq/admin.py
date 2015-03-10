from django.contrib import admin
from models import TaskQ

admin.site.register(TaskQ)
"""
# Register your models here.

@admin.register(TaskQ)
class TaskQAdmin(admin.ModelAdmin):
    pass
"""
