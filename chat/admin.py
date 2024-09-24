# from django.contrib import admin
# from chat.models import Conversation, Message, UploadedImage
# import os
# @admin.register(Conversation)
# class ConversationAdmin(admin.ModelAdmin):
#     list_display = ('user1', 'user2', 'created_at', 'last_message_timestamp')  # Add 'status' if included in the model
#     search_fields = ('user1__username', 'user2__username')
#     # list_filter = ('status',)  # Filter conversations by status

# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ('sender', 'conversation', 'timestamp', 'short_content')
#     search_fields = ('sender__username', 'conversation__id')
    
#     def short_content(self, obj):
#         return obj.content[:50]  # Show first 50 characters of the content
#     short_content.short_description = 'Content'  # Set a short description for the column

# @admin.register(UploadedImage)
# class UploadedImageAdmin(admin.ModelAdmin):
#     list_display = ('image_name', 'uploaded_at')
#     search_fields = ('image',)

#     def image_name(self, obj):
#         return os.path.basename(obj.image.name)  # Show only the file name
#     image_name.short_description = 'Image Name'  # Set a short description for the column

