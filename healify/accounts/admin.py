from django.contrib import admin

# Register your models here.
from accounts.models import Patient

admin.site.register(Patient)

