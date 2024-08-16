from django.contrib import admin

# Register your models here.
from creator.models import CreatorApproval
class CreatorApprovalAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'status')

    def save_model(self, request, obj, form, change):
        # Check if the status has changed
        if change and 'status' in form.changed_data:
            old_status = CreatorApproval.objects.get(pk=obj.pk).status
            new_status = form.cleaned_data['status']
            if old_status != new_status:
                # Call the method to create a notification and send a WebSocket message
                obj.create_notification_and_send_message(request.user)
        
        super().save_model(request, obj, form, change)

admin.site.register(CreatorApproval,CreatorApprovalAdmin)