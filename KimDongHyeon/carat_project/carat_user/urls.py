from django.urls import path
from . import views

urlpatterns = [
    path('', views.sign_up),
    path('auth', views.sign_in),
    path('hello/', views.hello),
]
