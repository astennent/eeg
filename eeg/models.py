from django.db import models
from django.contrib.auth.models import User

WAVE_TYPES = (
	(1, 'High Alpha'),
	(2, 'High Beta'), 
	(3, 'Mid Gamma'),
	(4, 'Low Alpha'),
	(5, 'Low Beta'),
	(6, 'Low Gamma'),
	(7, 'Delta'),
	(8, 'Theta'),
)

EMOTIONS = (
    (1, 'Happy'), 
    (2, 'Sad'), 
    (3, 'Angry'), 
    (4, 'Anxious'), 
    (5, 'Excited'), 
    (6, 'Pain'), 
)

class DataPoint(models.Model):
    wave = models.PositiveIntegerField(choices = WAVE_TYPES)
    user = models.ForeignKey(User, related_name='+')
    time = models.DateTimeField()
    value = models.PositiveIntegerField()

    # Formats the timestamp as a javascript Date object
    def js_time(self):
        return self.time.strftime("new Date(%Y, %m, %d, %H, %M, %S)")

class EmotionPoint(models.Model):
    emotion = models.PositiveIntegerField(choices=EMOTIONS)
    user = models.ForeignKey(User, related_name='+')
    time = models.DateTimeField()
