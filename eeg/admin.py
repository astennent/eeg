from django.contrib import admin
from eeg.models import *

class ExampleModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number', )


admin.site.register(ExampleModel, ExampleModelAdmin)
