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

