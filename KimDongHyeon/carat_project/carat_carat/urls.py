from django.urls import path, include
from . import views

carat_patterns = [
    path('<int:id>', views.do_carat.as_view()),
    path('<int:id>/list', views.read_carat_list.as_view())
]

caring_patterns = [
    path('', views.create_caring.as_view()),
    path('<int:id>', views.edit_caring.as_view())
]

timeline_patterns = [
    path('', views.read_timeline.as_view()),
    path('<email>', views.read_profile_timeline.as_view())
]

urlpatterns = [
    path('timeline/', include(timeline_patterns)),
    path('caring/', include(caring_patterns)),
    path('carat/', include(carat_patterns)),
    path('recaring/', views.do_recaring.as_view()),
]
