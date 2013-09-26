# coding: utf-8
import os
import sys

path = '/home/ubuntu/eeg'

if path not in sys.path:
  sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'eeg.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
