"""
WSGI config for fixit project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys

proj_dir = os.path.dirname(__file__)
main_proj_dir = os.path.join( proj_dir, '..')
taskq_dir = os.path.join(proj_dir, 'taskq')
if main_proj_dir not in sys.path:
    sys.path.append(main_proj_dir)

if proj_dir not in sys.path:
    sys.path.append(proj_dir)

if taskq_dir not in sys.path:
    sys.path.append(taskq_dir)

sys.path.append('/home/colama/web/venv/ve-fixit/lib/python2.7/site-packages/django')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fixit.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
