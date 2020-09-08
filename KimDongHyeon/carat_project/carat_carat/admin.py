from django.contrib import admin
from .models import *

# TODO 에러 response 제대로 다 명시하기 + 명세서 전체 수정


class UsersAdmin(admin.ModelAdmin):
    list_display = ['email', 'hashed_password', 'created_at']


class CaringsAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'caring', 'image', 'created_at']


class CaratListAdmin(admin.ModelAdmin):
    list_display = ['carat_user_email', 'caring']


class ProfilesAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'name', 'profile_image', 'cover_image', 'about_me']


class FollowListAdmin(admin.ModelAdmin):
    list_display = ['follow_user_email', 'followed_user_email']


class RecaringsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_email', 'caring', 'created_at']


class RecaringsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_email', 'caring', 'created_at']


admin.site.register(Users, UsersAdmin)
admin.site.register(Carings, CaringsAdmin)
admin.site.register(Recarings, RecaringsAdmin)
admin.site.register(CaratList, CaratListAdmin)
admin.site.register(FollowList, FollowListAdmin)
admin.site.register(Profiles, ProfilesAdmin)
