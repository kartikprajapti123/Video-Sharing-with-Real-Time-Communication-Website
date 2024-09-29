from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework .authentication import BasicAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from video.models import Video
from video.serializer import VideoSerializer
from utils.pagination import Pagination
from rest_framework.decorators import action
# from user.models import User
from creator.models import CreatorApproval
# from video.serializer import PostReviewSerializer


class VideoViewSet(ModelViewSet):
    queryset = Video.objects.filter(deleted=0).order_by("-created_at")
    serializer_class = VideoSerializer
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
    
    def get_permissions(self):
        print('action',self.action)
        if self.action == 'retrieve' or self.action=='user_approved_posts' or self.action=='random_posts' or self.action=="search_video_approved" or self.action=='list' or self.action=="latest_posts":
            return [AllowAny()]
        
        
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
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
    
    @action(detail=False,methods=["GET"],url_path="search-video-approved")
    def search_video_approved(self,request,*args,**kwargs):
        queryset=self.filter_queryset(self.get_queryset())
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
        return Response({"success": True, "data": serializer.data})
    
            

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        data = request.data
        # Add the user ID to the data
        data["user"] = request.user.id
        data["created_by"] = request.user.id
        data["updated_by"] = request.user.id
        

        # Pass the combined data to the serializer
        serializer = VideoSerializer(
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
        instance.delete()
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
    
    @action(detail=False, methods=['get'], url_path='user-approved-posts', permission_classes=[AllowAny],authentication_classes=[])
    def user_approved_posts(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"success": False, "message": "user_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        queryset = self.filter_queryset(
            Video.objects.filter(user__id=user_id, status="approved", deleted=0).order_by("-created_at")
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({"success": True, "data": serializer.data})
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": True, "data": serializer.data})
    
    @action(detail=False, methods=['get'], url_path='random-posts', permission_classes=[AllowAny])
    def random_posts(self, request, *args, **kwargs):
        print("random_posts")
        try:
            # Get a count of all non-deleted posts
            total_posts = Video.objects.filter(deleted=0).count()
            if total_posts == 0:
                return Response(
                    {"success": False, "message": "No posts available."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get a random sample of posts
            sample_size = min(15, total_posts)  # Adjust sample size as needed
            random_posts = Video.objects.filter(deleted=0).order_by('?')[:sample_size]

            # Instantiate the pagination class and paginate the random posts
            paginator = Pagination()
            paginator.page_size = 10  # Set your desired page size
            page = paginator.paginate_queryset(random_posts, request)

            # Serialize and return the paginated posts
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(
                {"success": True, "data": serializer.data}
            )

        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
            
    @action(detail=False, methods=['get'], url_path='latest-posts', permission_classes=[AllowAny])
    def latest_posts(self, request, *args, **kwargs):
        try:
            # Get the latest 5 posts
            latest_posts = Video.objects.filter(deleted=0).order_by("-created_at")[:5]

            # Serialize the posts
            serializer = self.get_serializer(latest_posts, many=True)
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    

# class PostReviewViewSet(ModelViewSet):
#     queryset = PostReview.objects.filter(deleted=0).order_by("-created_at")
#     serializer_class = PostReviewSerializer
#     pagination_class = Pagination
#     filter_backends = [SearchFilter, OrderingFilter]
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [JWTAuthentication]

#     search_fields = [
#         "message",
#         "user__username",
#         "post__title",
#     ]
#     ordering_fields = ["created_at", "updated_at"]
    
    
            
#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())

#         no_pagination = request.query_params.get("no_pagination")

#         if no_pagination:
#             serializer = self.serializer_class(queryset, many=True)
#             return Response({"success": True, "data": serializer.data})

#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.serializer_class(page, many=True)
#             return self.get_paginated_response({"success": True, "data": serializer.data})

#         serializer = self.serializer_class(queryset, many=True)
#         return Response({"success": True, "data": serializer.data})

#     def create(self, request, *args, **kwargs):
#         data = request.data
#         data["user"] = request.user.id
#         data["created_by"] = request.user.id

#         serializer = self.serializer_class(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"success": True, "data": serializer.data,"message":"Your comment beeen successfully submitted"},
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(
#             {"success": False, "message": serializer.errors},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     def update(self, request, *args, **kwargs):
#         instance = self.get_object()
#         data = request.data
#         data["updated_by"] = request.user.id

#         serializer = self.serializer_class(instance, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"success": True, "data": serializer.data},
#                 status=status.HTTP_200_OK,
#             )
#         return Response(
#             {"success": False, "message": serializer.errors},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.deleted = 1  # Assuming you have a `deleted` field for soft deletion
#         instance.save()
#         return Response(
#             {"success": True, "message": "Post review deleted successfully."},
#             status=status.HTTP_200_OK,
#         )

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.serializer_class(instance)
#         return Response(
#             {"success": True, "data": serializer.data},
#             status=status.HTTP_200_OK,
#         )
        
#     @action(detail=False, methods=["get"], url_path="reviews-by-post",permission_classes=[AllowAny])
#     def get_reviews_by_post(self, request):
#         post_id = request.query_params.get("post_id")
        
#         if not post_id:
#             return Response(
#                 {"success": False, "message": "post_id query parameter is required."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
        
#         post_reviews = PostReview.objects.filter(post_id=post_id, deleted=0).order_by("-created_at")

#         # page = self.paginate_queryset(post_reviews)
#         # if page is not None:
#             # serializer = self.serializer_class(page, many=True)
#             # return self.get_paginated_response({"success": True, "data": serializer.data})

#         serializer = self.serializer_class(post_reviews, many=True)
#         return Response({"success": True, "data": serializer.data})
    
    