from django.urls import path, include
from . import views

carat_patterns = [
    path('<int:id>', views.do_carat),
    path('<int:id>/list', views.read_carat_list)
]

caring_patterns = [
    path('', views.create_caring),
    path('<int:id>', views.edit_caring)
]

timeline_patterns = [
    path('', views.read_timeline),
    path('<email>', views.read_profile_timeline)
]

urlpatterns = [
    path('timeline/', include(timeline_patterns)),
    path('caring/', include(caring_patterns)),
    path('carat/', include(carat_patterns)),
    path('recaring/', views.do_recaring),
]
