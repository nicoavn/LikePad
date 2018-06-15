from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.
from Like.models import Like
from Like.Exceptions import DailyVotesAlreadyGivenException, IllegalLikeException


def login_view(request):
    user = request.POST.get('user','')
    password = request.POST.get('password','')
    user = authenticate(username=user, password=password)
    if user:
        login(request, user)
        return render(request, "dashboard.html",{})
    return render(request, "login.html",{})

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
