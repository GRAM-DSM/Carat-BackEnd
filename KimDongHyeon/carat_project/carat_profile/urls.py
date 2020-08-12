from django.urls import path
from . import views

urlpatterns = [
    path('<email>', views.read_profile),
    path('', views.update_profile),
    path('<email>/following', views.following),
    path('<email>/followers', views.followers),
]