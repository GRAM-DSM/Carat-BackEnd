from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from . import models


@api_view(['GET'])
def read_profile(request, email):    # 유저의 프로필 정보 가져오기
    profile = models.Profiles.objects.filter(user_email=email)


@api_view(['PUT'])
def update_profile(request):        # 유저의 프로필 정보 수정하기
    pass


@api_view(['GET'])
def following(request, email):      # 유저의 팔로잉 목록 가져오기
    pass


@api_view(['GET'])
def followers(request, email):      # 유저의 팔로워 목록 가져오기
    pass
