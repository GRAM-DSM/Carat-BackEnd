from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['POST', 'GET'])
def login_out(request):
    if request.method == 'POST':     # 로그인 하기
        pass
    elif request.method == 'GET':    # 로그아웃 하기
        pass


@api_view(['POST', 'DELETE'])
def account(request):
    if request.method == 'POST':     # 회원가입 하기
        pass
    elif request.method == 'DELETE':    # 계정 탈퇴 하기
        pass
