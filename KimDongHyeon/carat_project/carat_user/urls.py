from django.urls import path
from . import views

urlpatterns = [
    path('', views.sign_up.as_view()),
    path('auth', views.sign_in.as_view()),
]
