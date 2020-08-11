from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token


@api_view(['POST', 'DELETE', 'GET'])
def sign_in(request):
    if request.method == 'POST':  # 로그인 하기
        obtain_jwt_token()
    elif request.method == 'GET':  # 토큰 갱신 하기
        refresh_jwt_token()
    elif request.method == 'DELETE':  # 로그아웃 하기
        pass


@api_view(['POST', 'DELETE'])
def sign_up(request):
    if request.method == 'POST':  # 회원가입 하기
        pass
    elif request.method == 'DELETE':  # 계정 탈퇴 하기
        pass
