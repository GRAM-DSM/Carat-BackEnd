from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_caring),
    path('<int:id>', views.edit_caring)
]
