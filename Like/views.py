from django.contrib.auth.models import User
from django.shortcuts import render

from datetime import datetime as dt

from Like.models import Like
from Like.Exceptions import DailyVotesAlreadyGivenException, IllegalLikeException


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
        'error': error,
    }

    return render(request, "dashboard.html", context)
