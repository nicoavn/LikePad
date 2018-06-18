from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from Like.models import Like
from Like.Exceptions import DailyVotesAlreadyGivenException, IllegalLikeException


def login_view(request):
    return render(request, "login.html",{})

def signup_view(request):
    return render(request, "signup.html",{})

def login_api(request):
    user = request.POST.get('user', '')
    password = request.POST.get('password', '')
    user_found = authenticate(username=user, password=password)

    if user_found:
        login(request, user_found)
        return redirect(home)
    else:
        return render(request, "login.html",{'error':'Usuario y/o Password invalidos'})

def signup_api(request):
    password = request.POST.get('password', '')
    name = request.POST.get('name', '')
    last_name = request.POST.get('lastName', '')
    email = request.POST.get('email', '')

    try:
        user_created = User.objects.create_user(username=email,email=email,first_name=name,last_name=last_name,password=password)
    except Exception as e :
        return render(request, "signup.html", {"error":"Datos incorrectos"})

    if user_created:
        return render(request, "login.html", {})

    return render(request, "signup.html", {})

def signup_view(request):
    return render(request, "signup.html",{})


@login_required(login_url="/")
def home(request):
    users = User.objects.all()

    context = {
        'users': users
    }

    return render(request, "dashboard.html", context)

@login_required(login_url="/")
def like(request):
    report_to_id = int(request.POST.get('report_to_id', ''))

    report_to = None
    try:
        report_to = User.objects.get(id=report_to_id)
    except User.DoesNotExist:
        pass

    error = None
    try:
        Like.report(reporter=request.user, report_to=report_to)
    except DailyVotesAlreadyGivenException:
        error = 'Ha agotado sus like disponibles para hoy.'
    except IllegalLikeException:
        error = 'Sucio'

    users = User.objects.all()

    context = {
        'users': users,
        'error': error
    }

    return render(request, "dashboard.html", context)
