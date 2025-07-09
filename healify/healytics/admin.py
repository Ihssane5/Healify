from django.contrib import admin

# Register your models here.
from healytics.models import MedicalRecord
from healytics.models import MedicalChat
from healytics.models import History


admin.site.register(MedicalRecord)
admin.site.register(MedicalChat)
admin.site.register(History)
