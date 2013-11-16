from django.contrib import admin
from wolves.models import *

class BadgeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'points',)

class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'cycle_length', 'in_progress', 'is_day')
    
    def is_day(self, obj):
        return obj.is_day()

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'is_dead', 'is_wolf')

class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'experience')

admin.site.register(Player, PlayerAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Badge, BadgeAdmin)
admin.site.register(Account, AccountAdmin)

