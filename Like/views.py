from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout

from datetime import datetime as dt

from django.urls import reverse

from Like.models import Like, Debts
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


def calculate_strickes(stricks):
    n = 0
    pesos = 0
    for strick in range(stricks):
        n = n+1
        if n == 5:
            pesos = pesos + 50
        if n > 5:
            pesos = pesos + 5
    return pesos


@login_required(login_url="/")
def home(request, context=None):
    users = User.objects.all()
    message = request.GET.get("message", '')
    now = dt.now()
    datetime_day_start = dt(now.year, now.month, now.day)
    datetime_day_end = dt(now.year, now.month, now.day, 23, 59, 59)
    day_strickes_users = request.user.likes_given.filter(when__range=(datetime_day_start, datetime_day_end),
                                                         deleted_at__isnull=True).values_list('reported_to_id', flat=True)
    all_stricks_users = []
    daily_stricks = []
    for user in users:
        user.day_strickes = len(Like.get_day_likes(user))
        user.all_debs_pesos = len(Like.get_week_likes(user))
        user.pesos = calculate_strickes(len(Like.get_week_likes(user)))
        if user == request.user:
            continue

        if user.id in day_strickes_users:
            daily_stricks.append(user.id)

    if not context:
        context = {}
    context['users'] = users
    context['liked_users'] = daily_stricks
    context['week_likes'] = all_stricks_users
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

        strickes = len(Like.get_day_likes(report_to))
        today_user_debs = Debts.get_day_user_debs(report_to)
        if strickes >= 5:
            if len(today_user_debs) > 0:
                today_user_debs.update(quantity=calculate_strickes(strickes))
            else:
                Debts.save_user_debs(user=report_to, quantity=calculate_strickes(strickes))

    except DailyVotesAlreadyGivenException:
        error = 'Ha agotado sus like disponibles para hoy.'
    except AlreadyLikedUserException:
        error = 'No se permite dar like más de un like por usuario.'

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
        Debts.delete_user_debs(user=undo_report_to)
    except Exception as e:
        error = str(e)

    return redirect(home)


@login_required(login_url="/")
def awards(request):
    context = {
        'users': Like.get_week_awards()
    }
    return JsonResponse(context, safe=False)
