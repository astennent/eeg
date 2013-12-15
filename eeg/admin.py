from django.contrib import admin
from eeg.models import *

class DataPointAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wave', 'value','time')
    list_filter = ('user','wave',)

class EmotionPointAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'emotion', 'time',)
    list_filter = ('user', 'emotion',)

admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(EmotionPoint, EmotionPointAdmin)
