from django.contrib import admin

# Register your models here.
from assistant_medical.models import Conversation
from assistant_medical.models import Message
from assistant_medical.models import Patient




admin.site.register(Conversation)
admin.site.register(Message)

