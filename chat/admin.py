from django.contrib import admin

# Register your models here.
from chat.models import Conversation,Message,UploadedImage

admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(UploadedImage)
