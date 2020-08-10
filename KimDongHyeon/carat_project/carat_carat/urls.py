from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>', views.do_carat),
    path('<int:id>/list', views.read_carat_list)
]
