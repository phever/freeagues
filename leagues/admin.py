from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(EventResult)
admin.site.register(Event)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(Round)
admin.site.register(League)
