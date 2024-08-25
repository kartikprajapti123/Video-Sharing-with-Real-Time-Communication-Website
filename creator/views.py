from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from creator.models import CreatorApproval
from creator.serializer import CreatorApprovalSerializer
from utils.pagination import Pagination

class CreatorApprovalViewSet(ModelViewSet):
    queryset = CreatorApproval.objects.filter(deleted=0).order_by("-created_at")
    serializer_class = CreatorApprovalSerializer
    pagination_class = Pagination
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    search_fields = ['user__email', 'status', 'gender']
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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        existing_approval = CreatorApproval.objects.filter(created_by=request.user,deleted=0).first()
        
        if existing_approval:
            # If the user already has an entry, return the existing data
            serializer = self.serializer_class(existing_approval)
            return Response(
                {"success": True, "message": "User has already created a CreatorApproval entry.", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        data = request.data
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        data["updated_by"] = request.user.id
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
        instance.deleted = 1
        instance.save()
        return Response(
            {"success": True, "message": "Creator approval deleted successfully."},
            status=status.HTTP_200_OK,
        )
        
    @action(detail=False, methods=['post'], url_path='delete-creator')
    def delete_creator(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {"success": False, "message": "User ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            instance = CreatorApproval.objects.get(user_id=user_id, deleted=0).delete()
            # instance.deleted = 1
            # instance.status='Canceled'
            # instance.save()
            return Response(
                {"success": True, "message": "Creator approval deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except CreatorApproval.DoesNotExist:
            return Response(
                {"success": False, "message": "Creator approval not found or already deleted."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False,methods=['POST'],url_path='create_approval_status')
    def create_approval_status(self,request,*args, **kwargs):
        user_id = request.data.get('user')

        if not user_id:
            return Response(
                {"success": False, "message": "User ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for existing CreatorApproval record
        existing_approval = CreatorApproval.objects.filter(user_id=user_id, deleted=0).first()

        if existing_approval:
            # If the approval exists, return its status
            return Response(
                {"success": True, "status": existing_approval.status},
                status=status.HTTP_200_OK
            )

        else:
            
        # If no existing approval, create a new one
            return Response(
                {"success": True, "status": "None"},
                status=status.HTTP_200_OK,
            )

