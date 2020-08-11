import json
import bcrypt  # 암호화 용
import jwt  # 토큰 발행용

from carat_project.settings import SECRET_KEY  # 토큰 발행에 사용할 secret key
from .models import Users

from django.views import View
from django.http import JsonResponse, HttpResponse

from django.utils import timezone


class sign_up(View):
    def post(self, request):
        """ 계정 생성(회원 가입) 메소드 """
        data = json.loads(request.body)
        try:
            if Users.objects.filter(email=data['email']).exists():  # 존재하는 이메일인지 확인
                return JsonResponse({"message": "이미 존재하는 이메일 입니다!"}, status=400)
            # 비밀번호 암호화=====
            password = data['password'].encode('utf-8')  # 입력된 패스워드를 바이트 형태로 인코딩
            password_crypt = bcrypt.hashpw(password, bcrypt.gensalt())  # 암호화된 비밀번호 생성
            password_crypt = password_crypt.decode('utf-8')  # DB에 저장할 수 있는 유니코드 문자열 형태로 디코딩
            # =================
            Users(
                email=data['email'],
                password=password_crypt,  # 암호화된 비밀번호를 DB에 저장
                created_at=timezone.now()
            ).save()
            return HttpResponse(status=200)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!"}, status=400)

    def delete(self, request):
        """ 계정 삭제(회원 탈퇴) 메소드 """
        data = json.loads(request.body)
        try:
            if Users.objects.filter(email=data['email']).exists():  # 존재하는 이메일인지 확인
                return JsonResponse({"message": "이미 존재하는 이메일 입니다!"}, status=400)
            # ===비밀번호 암호화===
            password = data['password'].encode('utf-8')  # 입력된 패스워드를 바이트 형태로 인코딩
            password_crypt = bcrypt.hashpw(password, bcrypt.gensalt())  # 암호화된 비밀번호 생성
            password_crypt = password_crypt.decode('utf-8')  # DB에 저장할 수 있는 유니코드 문자열 형태로 디코딩
            # ==================
            Users(
                email=data['email'],
                password=password_crypt,  # 암호화된 비밀번호를 DB에 저장
                created_at=timezone.now()
            ).save()
            return HttpResponse(status=200)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!"}, status=400)


class sign_in(View):
    def post(self, request):
        data = json.loads(request.body)
        try:
            if Users.objects.filter(email=data['email']).exists():
                user = Users.objects.get(email=data['email'])

                if bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
                    # ===토큰 생성===      jwt.encode({<유저정보>}, <시크릿키>, algorithm = '특정 알고리즘')
                    token = jwt.encode({'email': data['email']}, SECRET_KEY, algorithm="HS256")
                    token = token.decode('utf-8')  # 유니코드 문자열로 디코딩
                    # =============
                    return JsonResponse({"token": token}, status=200)
                else:
                    return JsonResponse({"message": "비밀번호가 잘못되었습니다!"}, status=401)
            return JsonResponse({"message": "존재하지 않는 이메일입니다!"}, status=401)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!"}, status=400)


class TokenCheckView(View):
    def post(self, request):
        data = json.loads(request.body)

        user_token_info = jwt.decode(data['token'], SECRET_KEY, algorithm='HS256')

        if Users.objects.filter(email=user_token_info['email']).exists():
            return HttpResponse(status=200)

        return HttpResponse(status=403)


from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token


@api_view(['POST', 'DELETE', 'GET'])
def login_out(request):
    if request.method == 'POST':  # 로그인 하기
        obtain_jwt_token()
    elif request.method == 'GET':  # 토큰 갱신 하기
        refresh_jwt_token()
    elif request.method == 'DELETE':  # 로그아웃 하기
        pass


@api_view(['POST', 'DELETE'])
def account(request):
    if request.method == 'POST':  # 회원가입 하기

        pass
    elif request.method == 'DELETE':  # 계정 탈퇴 하기
        pass
