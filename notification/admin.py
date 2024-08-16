from django.contrib import admin
from notification.models import Notification,MainNotification
# Register your models here.
admin.site.register(Notification)
admin.site.register(MainNotification)
