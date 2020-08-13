from django.urls import path
from . import views

urlpatterns = [
    path('<email>', views.read_profile.as_view()),
    path('', views.update_profile.as_view()),
    path('<email>/following', views.following),
    path('<email>/followers', views.followers),
]