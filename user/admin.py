from django.contrib import admin
from django.contrib.admin import AdminSite
from video.models import Video
from django.contrib.auth.admin import UserAdmin
from .models import User
from pages.models import Pages
from notification.models import Notification, MainNotification
from creator.models import CreatorApproval
from chat.models import Conversation, Message, UploadedImage
from django.db import models
import os

# Custom Admin Site for Creators
class CreatorAdminSite(AdminSite):
    site_header = "Admin Administration"
    site_title = "Admin Portal"
    index_title = "Welcome to the Admin Management"

creator_admin_site = CreatorAdminSite(name='creator_admin')

# Custom Admin Site for Admin Administration
class AdminAdminSite(AdminSite):
    site_header = "Admin Administration"
    site_title = "Admin Portal"
    index_title = "Welcome to the Admin Management"

admin_admin_site = AdminAdminSite(name='admin_admin')

# Register models to the Creator Admin site
@admin.register(Video)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'user__email', 'status')

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            old_status = Video.objects.get(pk=obj.pk).status
            new_status = form.cleaned_data['status']
            if old_status != new_status:
                # Call the method to create a notification and send a WebSocket message
                obj.create_notification_and_send_message(request.user)

        super().save_model(request, obj, form, change)

creator_admin_site.register(Video, PostAdmin)

@admin.register(CreatorApproval)
class CreatorApprovalAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'status')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Order by status, placing 'pending' first, and then by created_at
        qs = qs.order_by(models.Case(
                models.When(status='pending', then=0),
                default=1,
                output_field=models.IntegerField()
            ), '-created_at')
        return qs
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            old_status = CreatorApproval.objects.get(pk=obj.pk).status
            new_status = form.cleaned_data['status']
            if old_status != new_status:
                obj.create_notification_and_send_message(request.user)
        super().save_model(request, obj, form, change)

creator_admin_site.register(CreatorApproval, CreatorApprovalAdmin)

# Register models to the Admin Administration site
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

admin_admin_site.register(User, CustomUserAdmin)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'sender_type', 'notification_type', 'is_read', 'timestamp', 'count')
    list_filter = ('sender_type', 'notification_type', 'is_read', 'timestamp')
    search_fields = ('sender__username', 'message')
    ordering = ['-timestamp']
    readonly_fields = ('timestamp',)

    def short_message(self, obj):
        return f"{obj.message[:30]}..." if len(obj.message) > 30 else obj.message
    short_message.short_description = 'Message'

admin_admin_site.register(Notification, NotificationAdmin)

@admin.register(MainNotification)
class MainNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_read', 'timestamp', 'link')
    list_filter = ('is_read', 'timestamp')
    fields = ('user', 'message', 'link')
    search_fields = ('user__username', 'message')
    ordering = ['-timestamp']
    readonly_fields = ('timestamp',)

    def short_message(self, obj):
        return f"{obj.message[:30]}..." if len(obj.message) > 30 else obj.message
    short_message.short_description = 'Message'

creator_admin_site.register(MainNotification, MainNotificationAdmin)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created_at', 'last_message_timestamp')
    search_fields = ('user1__username', 'user2__username')

admin_admin_site.register(Conversation, ConversationAdmin)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'timestamp', 'short_content')
    search_fields = ('sender__username', 'conversation__id')

    def short_content(self, obj):
        return obj.content[:50]  # Show first 50 characters of the content
    short_content.short_description = 'Content'

admin_admin_site.register(Message, MessageAdmin)

@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('image_name', 'uploaded_at')
    search_fields = ('image',)

    def image_name(self, obj):
        return os.path.basename(obj.image.name)
    image_name.short_description = 'Image Name'

admin_admin_site.register(UploadedImage, UploadedImageAdmin)

@admin.register(Pages)
class PagesAdmin(admin.ModelAdmin):
    list_display = ('page_name', 'page_url', 'show_in_menu','show_in_footer')
    search_fields = ('page_name',)
    fields = ('page_name', 'page_url', 'show_in_menu','show_in_footer','content')
    ordering = ('page_name',)

creator_admin_site.register(Pages, PagesAdmin)
