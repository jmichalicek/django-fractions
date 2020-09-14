from django.contrib import admin

# Register your models here.
from .models import TestModel

admin.site.register(TestModel)
