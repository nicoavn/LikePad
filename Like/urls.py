from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view),
    path('like', views.like),
    path('dislike', views.dislike),
    path('home', views.home),
]
