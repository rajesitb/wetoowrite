from django.contrib import admin
from .models import LoggedRecord, Profile

# Register your models here.
admin.site.register(LoggedRecord)


admin.site.register(Profile)
