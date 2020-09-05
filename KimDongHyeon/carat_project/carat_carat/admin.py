from django.contrib import admin
from .models import *

# TODO 프로필 이미지, 커버 이미지 처리 (view, model 둘다 수정)
# TODO 에러 response 제대로 정리
# TODO 루트 링크 페이지 만들기
# TODO 개발 다 끝났으면 디버그 모드 끄기
# TODO 리캐링 목록 API 만들기


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['email', 'hashed_password', 'created_at']


@admin.register(Carings)
class CaringsAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'caring', 'image', 'created_at']


@admin.register(CaratList)
class CaratListAdmin(admin.ModelAdmin):
    list_display = ['carat_user_email', 'caring']


@admin.register(Profiles)
class ProfilesAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'name', 'profile_image', 'cover_image', 'about_me']


@admin.register(FollowList)
class FollowListAdmin(admin.ModelAdmin):
    list_display = ['follow_user_email', 'followed_user_email']


@admin.register(Recarings)
class RecaringsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_email', 'caring', 'created_at']
