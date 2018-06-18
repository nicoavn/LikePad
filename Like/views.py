from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from datetime import datetime as dt

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

    now = dt.now()
    datetime_day_start = dt(now.year, now.month, now.day)
    datetime_day_end = dt(now.year, now.month, now.day, 23, 59, 59)
    day_liked_users = request.user.likes_given.filter(when__range=(datetime_day_start, datetime_day_end)
                                                      ).values_list('reported_to_id', flat=True)

    liked_users = []
    for user in users:
        if user == request.user:
            continue

        if user.id in day_liked_users:
            liked_users.append(user.id)

    context = {
        'users': users,
        'liked_users': liked_users,
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
        error = 'No se permite dar like a uno mismo.'

    context = {
        'error': error,
    }

    return redirect('Like.views.home', context)


@login_required(login_url="/")
def dislike(request):
    undo_report_to_id = int(request.POST.get('report_to_id', ''))

    undo_report_to = None
    try:
        undo_report_to = User.objects.get(id=undo_report_to_id)
    except User.DoesNotExist:
        pass

    error = None
    try:
        Like.undo_report(reporter=request.user, report_to=undo_report_to)
    except Exception as e:
        error = str(e)

    context = {
        'error': error,
    }

    return redirect('Like.views.home', context)
