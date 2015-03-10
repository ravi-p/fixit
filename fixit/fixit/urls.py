from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls import handler400, handler403
from django.conf.urls import handler404, handler500
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
admin.autodiscover()
urlpatterns = patterns('',
    # Examples:
    url(r'^$', RedirectView.as_view(url='/housekeep/')),

    url(r'^admin_profile/', include('admin_profile.urls')),

    url(r'^housekeep/', include('taskq.urls',namespace="housekeep",app_name="taskq")),
    url(r'^infra/', include('taskq.urls',namespace='infra',app_name='taskq')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social_auth.urls')),
    url(r'', include('django.contrib.auth.urls', namespace='auth')),
    url(r'^accounts/login/$', TemplateView.as_view(template_name = 'login.html')),
)

urlpatterns += staticfiles_urlpatterns()

handler400 = "fixit.views.handle400"
handler403 = "fixit.views.handle403"
handler404 = "fixit.views.handle404"
handler500 = "fixit.views.handle500"

