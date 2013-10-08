from django.db import models

class ExampleModel(models.Model):
    name = models.CharField(max_length=15)
    number = models.IntegerField();