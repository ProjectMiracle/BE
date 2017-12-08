from django.db import models
from django.contrib import admin

# Create your models here.
class Speech(models.Model):
    body = models.TextField()

class SpeechAdmin(admin.ModelAdmin):
    list_display = ('body')

admin.site.register(Speech)
