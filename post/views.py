from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from post.models import Post
from post.serializer import PostSerializer
from utils.pagination import Pagination
from rest_framework.decorators import action
# from user.models import User
from creator.models import CreatorApproval


class PostViewSet(ModelViewSet):
    queryset = Post.objects.filter(deleted=0).order_by("-created_at")
    serializer_class = PostSerializer
    pagination_class = Pagination
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    search_fields = [
        "title",
        "user__username",
        "status",
    ]
    ordering_fields = ["created_at", "updated_at", "status"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        print(queryset)
        no_pagination = request.query_params.get("no_pagination")
        status = request.query_params.get("status")
        title = request.query_params.get("title")
        user_username = request.query_params.get("user_username")

        if status:
            queryset = queryset.filter(status=status)

        if title:
            queryset = queryset.filter(title=title)

        if user_username:
            queryset = queryset.filter(user__username=user_username)

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
        return Response({"success": True, "data": serializer.data})

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        data = request.data
        # Add the user ID to the data
        data["user"] = request.user.id
        data["created_by"] = request.user.id

        # Pass the combined data to the serializer
        serializer = PostSerializer(
            data=data
        )  # Automatically associate the post with the current user

        # Merge data and files

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

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
        request.data._mutable = True

        instance = self.get_object()
        data = request.data
        data["updated_by"] = request.user.id
        serializer = self.serializer_class(instance, data=data, partial=True)

        if serializer.is_valid():
            has_changes = any(
                getattr(instance, field) != serializer.validated_data.get(field)
                for field in serializer.validated_data
            )
            print(has_changes)

            if has_changes:
                # If changes were made, set the status to "pending"
                serializer.save(status="pending")
                
                
            return Response(
                {"success": True, "data": serializer.data, "changes": has_changes},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = 1  # Assuming you have a `deleted` field for soft deletion
        instance.save()
        return Response(
            {"success": True, "message": "Post deleted successfully."},
            status=status.HTTP_200_OK,
        )
        
    @action(detail=False, methods=['get'], url_path='check-approval')
    def check_approval(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"success": False, "message": "user_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            creator = CreatorApproval.objects.get(user=user_id,status="approved")
            return Response(
                {"success": True, "message": "you are a creator",},
                status=status.HTTP_200_OK,
            )
        except CreatorApproval.DoesNotExist:
            return Response(
                {"success": False, "message": "You are not a creator."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
