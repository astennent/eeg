from django.contrib import admin
from eeg.models import *

class DataPointAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wave', 'value','time')
    list_filter = ('user','wave',)

admin.site.register(DataPoint, DataPointAdmin)
