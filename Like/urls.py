from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view),
    path('login', views.login_api),
    path('signup', views.signup_api),
    path('signup/view', views.signup_view),
    path('like', views.like),
    path('home', views.home),
]
