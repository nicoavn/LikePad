from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout

from datetime import datetime as dt

from django.urls import reverse

from Like.models import Like
from Like.Exceptions import DailyVotesAlreadyGivenException, IllegalLikeException, AlreadyLikedUserException


def login_view(request):
    try:
        if request.user.is_authenticated():
            return  redirect(home)
    except:
        pass
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
        return render(request, "login.html", {'error': 'Usuario y/o Password invalidos'})


def signup_api(request):
    password = request.POST.get('password', '')
    name = request.POST.get('name', '')
    last_name = request.POST.get('lastName', '')
    email = request.POST.get('email', '')

    user_found = User.objects.filter(email=email)
    if user_found:
        return render(request, "signup.html", {"error": "Email no disponible"})

    try:
        user_created = User.objects.create_user(username=email,email=email,first_name=name,last_name=last_name,password=password)
    except:
        return render(request, "signup.html", {"error":"Datos incorrectos"})

    if user_created:
        return render(request, "login.html", {})

    return render(request, "signup.html", {})


@login_required(login_url="/")
def log_out(request):
    logout(request)
    return redirect(home)


@login_required(login_url="/")
def home(request, context=None):
    users = User.objects.all()
    message = request.GET.get("message", '')
    now = dt.now()
    datetime_day_start = dt(now.year, now.month, now.day)
    datetime_day_end = dt(now.year, now.month, now.day, 23, 59, 59)
    day_liked_users = request.user.likes_given.filter(when__range=(datetime_day_start, datetime_day_end),
                                                      deleted_at__isnull=True
                                                      ).values_list('reported_to_id', flat=True)

    liked_users = []
    for user in users:
        user.day_likes = len(Like.get_day_likes(user))
        user.week_likes = len(Like.get_week_likes(user))

        if user == request.user:
            continue

        if user.id in day_liked_users:
            liked_users.append(user.id)

    if not context:
        context = {}
    context['users'] = users
    context['liked_users'] = liked_users
    context['week_likes'] = liked_users
    context['error'] = message if message else ''


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
    except AlreadyLikedUserException:
        error = 'No se permite dar like más de un like por usuario.'
    # except Exception:
    #     error = 'Este... Hay que debuguear.'

    return redirect("/home?message="+str(error if error else ''))


@login_required(login_url="/")
def dislike(request):
    undo_report_to_id = int(request.POST.get('report_to_id', ''))

    undo_report_to = None
    try:
        undo_report_to = User.objects.get(id=undo_report_to_id)
    except User.DoesNotExist:
        pass

    try:
        Like.undo_report(reporter=request.user, report_to=undo_report_to)
    except Exception as e:
        error = str(e)

    return redirect(home)


@login_required(login_url="/")
def awards(request):
    context = {
        'users': Like.get_week_awards()
    }
    return JsonResponse(context, safe=False)
