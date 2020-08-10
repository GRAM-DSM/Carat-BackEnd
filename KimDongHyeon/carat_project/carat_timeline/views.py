from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def read_timeline(request):      # 타임라인 가져오기
    pass


@api_view(['GET'])
def read_profile_timeline(request, email):    # 프로필 타임라인 가져오기
    pass
