from rest_framework.routers import DefaultRouter
from user.views import RegisterViewSet,VerifyEmailViewset,LoginViewSet,ForgotPasswordViewSet,ChangePasswordViewSet,LoginWithGoogleViewSet

routers=DefaultRouter()

routers.register(r'register',RegisterViewSet,basename="register")
# routers.register(r'verify-email/(?P<token>[\w\.-]+)',VerifyEmailViewset,basename="verify-email")
routers.register(r'login',LoginViewSet,basename="Login")
routers.register(r'forgot-password',ForgotPasswordViewSet,basename="forgot-password")
routers.register(r'change-password',ChangePasswordViewSet,basename="change-password")
routers.register(r'google-authentication',LoginWithGoogleViewSet,basename="google-authentication")




