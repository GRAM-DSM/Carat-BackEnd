from django.urls import path, include
from . import views

carat_patterns = [
    path('<id>', views.do_carat.as_view()),
    path('<id>/list', views.read_carat_list.as_view())
]

caring_patterns = [
    path('', views.create_caring.as_view()),
    path('<int:id>', views.edit_caring.as_view()),
    path('<id>/detail', views.detail_caring.as_view())
]

timeline_patterns = [
    path('', views.read_timeline.as_view()),
    path('caring/<email>', views.read_profile_caring_timeline.as_view()),
    path('carat/<email>', views.read_profile_carat_timeline.as_view())
]

recaring_patterns = [
    path('', views.create_recaring.as_view()),
    path('<id>', views.delete_recaring.as_view()),
    path('<id>/list', views.read_recaring_list.as_view())
]

urlpatterns = [
    path('timeline/', include(timeline_patterns)),
    path('caring/', include(caring_patterns)),
    path('carat/', include(carat_patterns)),
    path('recaring/', include(recaring_patterns)),
    path('', views.hi.as_view())    # 이스터 에그?
]
