from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,"home.html")

def index(request):
    return render(request,"index.html")

def signin(request):
    return render(request,"login.html")

def signup(request):
    return render(request,"register.html")

def verify_otp(request,token):
    return render(request,"verification-code.html")

def forgot_password(request):
    return render(request,"forgot-password.html")

def reset_password(request,token):
    return render(request,"reset-password.html")

def myprofile(request):
    return render(request,"myprofile.html")
    
def others_profile(request,id):
    return render(request,"others-profile.html")

def contact_list(request):
    return render(request,"changes_chat.html")
    
def chatting(request,id):
    return render(request,"chatting.html")

def chatting2(request):
    return render(request,"chat_messages.html")

def notification(request):
    return render(request,"notification_user.html")
    
    

def become_creator(request):
    return render(request,"creator_become.html")

def terms_of_service(request):
    return render(request,"terms_of_service.html")


def upload_video(request):
    return render(request,"upload-video.html")
    


def support_ticket(request):
    return render(request,"support-tickets.html")
    

def my_video(request):
    return render(request,"my_video.html")


def myprofileedit(request):
    return render(request,"myprofileedit.html")
    
def changepassword(request):
    return render(request,"mychangepassword.html")
    

def mydeleteaccount(request):
    return render(request,"mydelete-account.html")
    
def updatevideo(request,id):
    return render(request,"update-video.html")
    

def video_view(request,id):
    return render(request,"video-view.html")

def search(request):
    return render(request,"search.html")
    
    
def other_video(request,id):
    return render(request,"other_video.html")

def myfollowers(request):
    return render(request,"myfollowers.html")
    
    
def myfollowing(request):
    return render(request,"myfollowing.html")
    
def followers(request,id):
    return render(request,"other_followers.html")
    
def following(request,id):
    return render(request,"other_following.html")
    
def pages_func(request,id):
    return render(request,"pages.html")

def custom_404_view(request, exception):
    return render(request, 'error-404.html', status=404)
    
    