from rest_framework.routers import DefaultRouter
from user.views import RegisterViewSet,VerifyEmailViewset,LoginViewSet,ForgotPasswordViewSet,ChangePasswordViewSet,LoginWithGoogleViewSet,UserViewSet

from chat.consumers import MyChatConsumer,GlobalChatConsumer
from notification.consumers import NotificationConsumer
from chat.views import ConversationViewSet,MessageViewSet,UplaodedImaeViewSet
from notification.views import NotificationViewSet,MainNotificationViewSet
from creator.views import CreatorApprovalViewSet
from video.views import VideoViewSet
from follow.views import FollowViewSet
from pages.views import PagesViewSet,FanPagesViewSet,SimultaneouslyPagesViewSet
from support_ticket.views import SupportTicketPagesViewSet
routers=DefaultRouter()

routers.register(r'register',RegisterViewSet,basename="register")
# routers.register(r'verify-email/(?P<token>[\w\.-]+)',VerifyEmailViewset,basename="verify-email")
routers.register(r'login',LoginViewSet,basename="Login")
routers.register(r'forgot-password',ForgotPasswordViewSet,basename="forgot-password")
routers.register(r'change-password',ChangePasswordViewSet,basename="change-password")
routers.register(r'google-authentication',LoginWithGoogleViewSet,basename="google-authentication")

routers.register(r'user',UserViewSet,basename='user')
routers.register(r'messages',MessageViewSet,basename='messages')
routers.register(r'conversations',ConversationViewSet,basename='conversation')
routers.register(r'uploads',UplaodedImaeViewSet,basename='upload-image')
routers.register(r'notification',NotificationViewSet,basename="notification")
routers.register(r'main-notification',MainNotificationViewSet,basename="main-notification")

routers.register(r'creator-approval',CreatorApprovalViewSet,basename="creator-approval")
routers.register(r'upload-video',VideoViewSet,basename="upload-video")
# routers.register(r'post-review',PostReviewViewSet,basename="post-review")
routers.register(r'follow',FollowViewSet,basename="follow")
routers.register(r'creator-page',PagesViewSet,basename="creator-page")
routers.register(r'fan-page',FanPagesViewSet,basename="fan-page")
routers.register(r'simultaneously-page',SimultaneouslyPagesViewSet,basename="page")
routers.register(r'support-ticket',SupportTicketPagesViewSet,basename="support-ticket")



from django.urls import path
websocket_urlpatterns=[
    path("ws/chat/<str:id>/",MyChatConsumer.as_asgi()),
    path("ws/notification/<str:uuid>/",NotificationConsumer.as_asgi()),
    path("ws/global_chat/<str:uuid>/",GlobalChatConsumer.as_asgi())
    
    
]