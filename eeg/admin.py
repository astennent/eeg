from django.contrib import admin
from eeg.models import *

class DataPointAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wave', 'value',)
    list_filter = ('user',)

admin.site.register(DataPoint, DataPointAdmin)
