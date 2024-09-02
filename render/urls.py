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
    path('user-profile/<str:id>/',views.others_profile,name="others-profile"),
    path('user-video/<str:id>/',views.other_video,name="others-video"),
    
    path('contact-list/',views.contact_list,name="chating"),
    path('chatting/<str:id>/',views.chatting,name="chating"),
    path('notification/',views.notification,name="notification"),
    path('chatting/',views.chatting2,name="chattting"),
    path('creator/',views.become_creator,name="become_creator"),
    path('terms_of_service/',views.terms_of_service,name="terms_of_service"),
    path('upload-video/',views.upload_post,name="uplaod_Post"),
    path('mypost/',views.my_post,name="my-post"),
    path('myprofileedit/',views.myprofileedit,name="my-post"),
    
    path('mychangepassword/',views.changepassword,name="my-post"),
    path('mydelete-account/',views.mydeleteaccount,name="my-post"),
    
    path('update-video/<str:id>/',views.updatepost,name="update-post"),
    path('post-view/<str:id>/',views.post_view,name="update-post"),
    path('search/',views.search,name="search"),
    
    # path('myfollowers/',views.myfollowers,name="followers"),
    # path('myfollowing/',views.myfollowing,name="following"),
    
    # path('following/<str:id>/',views.following,name="following"),
    # path('followers/<str:id>/',views.followers,name="followers")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
]