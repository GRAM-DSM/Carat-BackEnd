from django.urls import path
from . import views

urlpatterns = [
    path('<string:email>', views.read_profile),
    path('', views.update_profile),
    path('<string:email>/following', views.following),
    path('<string:email>/followers', views.followers)
]