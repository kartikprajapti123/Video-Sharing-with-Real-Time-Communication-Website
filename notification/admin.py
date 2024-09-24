# from django.contrib import admin
# from notification.models import Notification, MainNotification

# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     list_display = ('id', 'sender', 'sender_type', 'notification_type', 'is_read', 'timestamp', 'count')
#     list_filter = ('sender_type', 'notification_type', 'is_read', 'timestamp')
#     search_fields = ('sender__username', 'sender__username', 'message')
#     ordering = ['-timestamp']
#     readonly_fields = ('timestamp',)

#     # Custom method to display the first 30 characters of the message
#     def short_message(self, obj):
#         return f"{obj.message[:30]}..." if len(obj.message) > 30 else obj.message
#     short_message.short_description = 'Message'


# @admin.register(MainNotification)
# class MainNotificationAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'is_read', 'timestamp', 'link')
#     list_filter = ('is_read', 'timestamp')
#     search_fields = ('user__username', 'message')
#     ordering = ['-timestamp']
#     readonly_fields = ('timestamp',)

#     # Custom method to display the first 30 characters of the message
#     def short_message(self, obj):
#         return f"{obj.message[:30]}..." if len(obj.message) > 30 else obj.message
#     short_message.short_description = 'Message'


