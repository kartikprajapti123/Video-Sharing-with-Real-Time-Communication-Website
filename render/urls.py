from django.contrib import admin
from django.urls import path
from render import views


urlpatterns = [
    path('',views.home,name="home"),
    path('index/',views.index,name="index"),
    path('signin/',views.signin,name="signin"),
    path('signup/',views.signup,name="signup"),
    path('verify-otp/<str:token>/',views.verify_otp,name="signup"),
    path('forgot-password/',views.forgot_password,name="forgot_password"),
    path('reset-password/<str:token>/',views.reset_password,name="reset-password"),
    path('myprofile/',views.myprofile,name="my-profile"),
    path('profile/<str:id>/',views.others_profile,name="others-profile"),
    path('contact-list/',views.contact_list,name="chating"),
    path('chatting/<str:id>/',views.chatting,name="chating"),
    path('notification/',views.notification,name="notification"),
    
    
    
    
    
    
    
    
    
    
    
]