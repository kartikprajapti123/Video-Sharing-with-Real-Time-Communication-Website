from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from chat.models import Conversation, Message,UploadedImage
from chat.serializers import ConversationsSerializer, MessageSerializer,UploadedImageSerializer
from utils.pagination import Pagination
import os 
from rest_framework.decorators import action
from django.db.models import Q

class ConversationViewSet(ModelViewSet):
    queryset = Conversation.objects.filter(deleted=0).order_by("-created_at")
    serializer_class = ConversationsSerializer
    pagination_class = Pagination
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    search_fields = ['user1__username', 'user2__username']  # Example search fields, adjust as needed

    ordering_fields = ['created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        no_pagination = request.query_params.get("no_pagination")
        if no_pagination:
            serializer = self.serializer_class(queryset, many=True)
            return Response({"success": True, "data": serializer.data})

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(
                {"success": True, "data": serializer.data}
            )

        serializer = self.serializer_class(queryset, many=True)
        return self.get_paginated_response({"success": True, "data": serializer.data})

    def create(self, request, *args, **kwargs):
        data = request.data
        user1_id = data.get('user1')
        user2_id = data.get('user2')

        if not user1_id or not user2_id:
            return Response(
                {"success": False, "message": "User1 and User2 IDs are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure user1 is not the same as user2
        if user1_id == user2_id:
            return Response(
                {"success": False, "message": "A user cannot have a conversation with themselves."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for existing conversation
        existing_conversation = Conversation.objects.filter(
            (Q(user1_id=user1_id) & Q(user2_id=user2_id)) |
            (Q(user1_id=user2_id) & Q(user2_id=user1_id))
        ).first()

        if existing_conversation:
            existing_conversation.deleted = 0
            existing_conversation.save()
            return Response(
                {"success": True, "data": ConversationsSerializer(existing_conversation).data},
                status=status.HTTP_200_OK
            )

        # Create a new conversation if it doesn't exist
        data["created_by"] = request.user.id
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        data["updated_by"] = request.user.id
        serializer = self.serializer_class(instance, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted=1
        instance.save()
        return Response(
            {"success": True, "message": "Conversation Deleted Successfully."},
            status=status.HTTP_200_OK,
        )
        
    @action(detail=False, methods=['get'], url_path="user-conversations")
    def user_conversations(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"success": False, "message": "User ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            conversations = Conversation.objects.filter(
                (Q(user1_id=user_id) | Q(user2_id=user_id)) & Q(deleted=0)
            ).order_by('-last_message_timestamp')

            # if not conversations.exists():
            #     return Response(
            #         {"success": False, "message": "No conversations found for this user."},
            #         status=status.HTTP_404_NOT_FOUND
            #     )
        except Conversation.DoesNotExist:
            return Response(
                {"success": False, "message": "No conversations found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(conversations, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )


class MessageViewSet(ModelViewSet):
    queryset = Message.objects.filter(deleted=0).order_by("-timestamp")
    serializer_class = MessageSerializer
    pagination_class = Pagination
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    search_fields = ['content', 'sender__username', 'conversation__id']

    ordering_fields = ['timestamp']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        no_pagination = request.query_params.get("no_pagination")
        if no_pagination:
            serializer = self.serializer_class(queryset, many=True)
            return Response({"success": True, "data": serializer.data})

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(
                {"success": True, "data": serializer.data}
            )

        serializer = self.serializer_class(queryset, many=True)
        return self.get_paginated_response({"success": True, "data": serializer.data})

    def create(self, request, *args, **kwargs):
        data = request.data
        data["sender"] = request.user.id
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.serializer_class(instance, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted=1
        instance.save()
        return Response(
            {"success": True, "message": "Message Deleted Successfully."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path="conversation-messages")
    def conversation_messages(self, request):
        conversation_id = request.query_params.get('conversation_id')
        if not conversation_id:
            return Response(
                {"success": False, "message": "Conversation ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Fetch messages for the given conversation_id
        messages = Message.objects.filter(conversation_id=conversation_id)
        
        if not messages.exists():
            return Response(
                {"success": True, "message": "No messages found for this conversation.", "data": []},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(messages, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )
        
    # @action(detail=False, methods=['get'], url_path="conversation-messages")
    # def conversation_messages(self, request):
    #     conversation_id = request.query_params.get('conversation_id')
    #     if not conversation_id:
    #         return Response({"success": False, "message": "Conversation ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    #     try:
    #         messages = Message.objects.filter(conversation_id=conversation_id)
    #     except Message.DoesNotExist:
    #         return Response({"success": False, "message": "No messages found for this conversation."}, status=status.HTTP_404_NOT_FOUND)
    #     serializer = self.get_serializer(messages, many=True)
    #     return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path="unread-messages")
    def get_unread_messages(self, request):
        conversation_id = request.query_params.get('conversation_id')
        user_id = request.user.id
        if not conversation_id:
            return Response({"success": False, "message": "Conversation ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            if conversation.user1_id == user_id:
                messages = Message.objects.filter(conversation_id=conversation_id, is_read_by_user1=False)
            elif conversation.user2_id == user_id:
                messages = Message.objects.filter(conversation_id=conversation_id, is_read_by_user2=False)
            else:
                return Response({"success": False, "message": "User not part of the conversation."}, status=status.HTTP_403_FORBIDDEN)
        except Conversation.DoesNotExist:
            return Response({"success": False, "message": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)
        except Message.DoesNotExist:
            return Response({"success": False, "message": "No unread messages found for this conversation."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(messages, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path="mark-messages-read")
    def mark_messages_read(self, request):
        conversation_id = request.data.get('conversation_id')
        user_id = request.user.id
        if not conversation_id:
            return Response({"success": False, "message": "Conversation ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            if conversation.user1_id == user_id:
                messages = Message.objects.filter(conversation_id=conversation_id, is_read_by_user1=False)
                messages.update(is_read_by_user1=True)
            elif conversation.user2_id == user_id:
                messages = Message.objects.filter(conversation_id=conversation_id, is_read_by_user2=False)
                messages.update(is_read_by_user2=True)
            else:
                return Response({"success": False, "message": "User not part of the conversation."}, status=status.HTTP_403_FORBIDDEN)
        except Conversation.DoesNotExist:
            return Response({"success": False, "message": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)
        except Message.DoesNotExist:
            return Response({"success": False, "message": "No unread messages found for this conversation."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "message": "All messages marked as read."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path="mark-message-read")
    def mark_message_read(self, request):
        message_id = request.data.get('message_id')
        print(message_id)
        user_id = request.user.id
        if not message_id:
            return Response({"success": False, "message": "Message ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            message = Message.objects.get(id=message_id)
            conversation = message.conversation
            if conversation.user1_id == user_id:
                message.is_read_by_user1 = True
            elif conversation.user2_id == user_id:
                message.is_read_by_user2 = True
            else:
                return Response({"success": False, "message": "User not part of the conversation."}, status=status.HTTP_403_FORBIDDEN)
            message.save()
        except Message.DoesNotExist:
            return Response({"success": False, "message": "Message not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "message": "Message marked as read."}, status=status.HTTP_200_OK)

class UplaodedImaeViewSet(ModelViewSet):
    queryset=UploadedImage.objects.all()
    serializer_class=UploadedImageSerializer
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    
    def create(self, request, *args, **kwargs):
        image = request.FILES.get("image")
        print(image)
        if not image:
            return Response({"success": False, "message": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file type
        valid_extensions = ['.jpg', '.jpeg', '.png']
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in valid_extensions:
            return Response({"success": False, "message": "Invalid file type. Only JPEG,JPG and PNG files are allowed."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the UploadedImage instance
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"success": False, "message": serializer.data}, status=status.HTTP_400_BAD_REQUEST)
    
    
    