from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from rest_framework.decorators import action
from notification.models import Notification,MainNotification
from notification.serializer import NotificationSerializer,MainNotificationSerializer
from utils.pagination import Pagination

class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.filter(deleted=0).order_by('-timestamp')
    serializer_class = NotificationSerializer
    pagination_class = Pagination
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    search_fields = ['user__username', 'message', 'notification_type']  # Example search fields, adjust as needed
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
        data['user'] = request.user.id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.serializer_class(instance, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = 1  # Assuming you have a field to soft-delete notifications
        instance.save()
        return Response(
            {"success": True, "message": "Notification Deleted Successfully."},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'],url_path="unread-for-user")
    def unread_for_user(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"success": False, "message": "user_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_id = int(user_id)
        except ValueError:
            return Response(
                {"success": False, "message": "user_id must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        unread_notifications = self.queryset.filter(user_id=user_id)
        serializer = self.serializer_class(unread_notifications, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )
        
    @action(detail=False, methods=['POST'], url_path="multiple-mark-as-read")
    def multiple_mark_as_read(self, request):
        user_id = request.data.get('user_id')
        common_uuid = request.data.get('common_uuid')
    
        if not user_id or not common_uuid:
            return Response(
                {"success": False, "message": "user_id and common_uuid are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
        try:
            user_id = int(user_id)
        except ValueError:
            return Response(
                {"success": False, "message": "user_id must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
        updated_count = Notification.objects.filter(
            user_id=user_id,
            common_uuid=common_uuid,
            is_read=False
        ).update(is_read=True)
    
        return Response(
            {"success": True, "message": f"Marked {updated_count} notifications as read."},
            status=status.HTTP_200_OK
        )
    @action(detail=False, methods=['POST'], url_path="single-mark-as-read")
    def single_mark_as_read(self, request):
        notification_id = request.data.get('notification_id')
        if notification_id is None:
            return Response(
                {"success": False, "message": "Notification ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            notification = Notification.objects.get(id=notification_id, deleted=0)
            notification.is_read = True
            notification.count=0
            notification.save()
            return Response(
                {"success": True, "message": "Notification marked as read."},
                status=status.HTTP_200_OK
            )
        except Notification.DoesNotExist:
            return Response(
                {"success": False, "message": "Notification not found."},
                status=status.HTTP_404_NOT_FOUND
            )

class MainNotificationViewSet(ModelViewSet):
    queryset = MainNotification.objects.filter(deleted=0).order_by('-timestamp')
    serializer_class = MainNotificationSerializer
    pagination_class = Pagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def create(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.serializer_class(instance, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
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


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = 1  # Assuming you have a field to soft-delete notifications
        instance.save()
        return Response(
            {"success": True, "message": "Main Notification Deleted Successfully."},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='notifications-for-user')
    def notifications_for_user(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"success": False, "message": "user_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
        try:
            user_id = int(user_id)
        except ValueError:
            return Response(
                {"success": False, "message": "user_id must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
        notifications = self.queryset.filter(user_id=user_id)
    
        # Serialize all notifications without pagination
        serializer = self.serializer_class(notifications, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )
    @action(detail=False, methods=['POST'], url_path="mark-all-user-notifications-read")
    def mark_all_user_notifications_read(self, request):
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"success": False, "message": "user_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_id = int(user_id)
        except ValueError:
            return Response(
                {"success": False, "message": "user_id must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter notifications for the specified user that are not deleted
        updated_count = MainNotification.objects.filter(
            user_id=user_id,
            deleted=0,
            is_read=False
        ).update(is_read=True)
        
        if updated_count == 0:
                return Response(
                {"success": False, "message": "All notifications are already marked as read."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"success": True, "message": f"Marked {updated_count} notifications as read."},
            status=status.HTTP_200_OK
        )