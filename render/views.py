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
    return render(request,"contact_list.html")
    
def chatting(request,id):
    return render(request,"chatting.html")
    

