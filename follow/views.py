from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from notification.models import MainNotification
from .models import Follow
from .serializers import FollowSerializer
from utils.pagination import Pagination
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.timezone import now



class FollowViewSet(ModelViewSet):
    queryset = Follow.objects.all().order_by("-created_at")
    serializer_class = FollowSerializer
    pagination_class = Pagination
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    search_fields = [
        "by_user_username",
        "by_user",
        "to_user",
        "to_user_username",
        "status",
    ]
    ordering_fields = ["created_at", "updated_at"]


    def get_permissions(self):
        if self.action=="list" :
            permission_classes=[AllowAny]
        
        else:
            permission_classes=[IsAuthenticated]
            
        return [permission() for permission in permission_classes]
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        by_user = request.query_params.get("by_user")

        if by_user:
            queryset = queryset.filter(by_user=by_user)

        # Filtering based on 'to_user'
        to_user = request.query_params.get("to_user")
        if to_user:
            queryset = queryset.filter(to_user=to_user)

        # Filtering based on 'status'
        status = request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        by_user_username = request.query_params.get("by_user_username")
        if by_user_username:
            queryset = queryset.filter(by_user__username__icontains=by_user_username)

        to_user_username = request.query_params.get("to_user_username")
        if to_user_username:
            queryset = queryset.filter(to_user__username__icontains=to_user_username)

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        data = request.data
        data["by_user"] = request.user.id

        existing_follow = Follow.objects.filter(
            by_user=request.user, to_user=data.get("to_user")
        ).first()
        if existing_follow:
            serializer = self.serializer_class(existing_follow)
            return Response(
                {
                    "success": True,
                    "message": "You are already following this user.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            followed_user = serializer.instance.to_user
            notification_message = f"<b>Follower Update:</b> You have a new follower: <b>{request.user.username}</b>."

            main_notification = MainNotification.objects.create(
                user=followed_user,
                message=notification_message,
                link=f"/myfollowers/"  # Adjust the link as needed
            )

            # Send WebSocket notification

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{followed_user.uuid}",
                {
                    'type': 'send_main_notification',
                    'notification_id': main_notification.id,
                    'message': notification_message,
                    'timestamp': str(now()),
                    'link': f"/myfollowers/",
                }
            )

            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.serializer_class(instance, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        followed_user = instance.to_user

        # Delete the follow relationship
        instance.delete()

        # Create a notification for the user being unfollowed
        notification_message = f"<b>Follower Update:</b> <b>{request.user.username}</b> has unfollowed you."

        main_notification = MainNotification.objects.create(
            user=followed_user,
            message=notification_message,
            link=f"/myfollowing/"  # Adjust the link as needed
        )

        # Send WebSocket notification
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{followed_user.uuid}",
            {
                'type': 'send_main_notification',
                'notification_id': main_notification.id,
                'message': notification_message,
                'timestamp': str(now()),
                'link': f"/myfollowing/",
            }
        )

        return Response(
            {"success": True, "message": "Follow relationship deleted successfully."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="unfollow")
    def unfollow(self, request):
        to_user_id = request.data("to_user_id")
        follow = Follow.objects.filter(
            by_user=request.user, to_user_id=to_user_id
        ).first()
        if follow:
            followed_user = follow.to_user
            follow.delete()
            notification_message = f"<b>Follower Update:</b> <b>{request.user.username}</b> has unfollowed you."
        
            main_notification = MainNotification.objects.create(
                user=followed_user,
                message=notification_message,
                link=f"/myfollowing/"  # Adjust the link as needed
            )

            # Send WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{followed_user.uuid}",
                {
                    'type': 'send_main_notification',
                    'notification_id': main_notification.id,
                    'message': notification_message,
                    'timestamp': str(now()),
                    'link': f"/myfollowing/",
                }
            )

            return Response(
                {"success": True, "message": "You have unfollowed the user."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "message": "Follow relationship does not exist."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["GET"], url_path="get-followers-following")
    def get_followers_following(self, request):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response(
                {"success": False, "message": "user id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        followers = Follow.objects.filter(to_user=user_id).count()
        following = Follow.objects.filter(by_user=user_id).count()

        data = {"followers": followers, "following": following}

        return Response({"success": True, "data": data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="user-is-following")
    def user_is_following(self, request, *args, **kwargs):
        by_user_id = request.user.id
        to_user_id = request.query_params.get("to_user")

        if not by_user_id or not to_user_id:
            return Response(
                {"success": False, "message": "Both by_user and to_user are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            follow_instance = Follow.objects.get(
                by_user=by_user_id, to_user=to_user_id, status="follow"
            )
        except Follow.DoesNotExist:
            return Response(
                {"success": False, "message": "Follow instance not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.serializer_class(follow_instance)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )
        
    # @action(detail=False, methods=["get"], url_path="user-is-following")
    # def user_is_following(self, request, *args, **kwargs):
    #     to_user_id = request.query_params.get("to_user")

    #     if not to_user_id:
    #         return Response(
    #             {"success": False, "message": "'to_user' is required"},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )

    #     # Check if the authenticated user is following the 'to_user'
    #     is_following = Follow.objects.filter(
    #         by_user=request.user.id, to_user_id=to_user_id, status="follow"
    #     ).exists()

    #     if is_following:
    #         return Response(
    #             {"success": True, "message": "User is following","data":},
    #             status=status.HTTP_200_OK,
    #         )
    #     else:
    #         return Response(
    #             {"success": False, "message": "User is not following"},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )
