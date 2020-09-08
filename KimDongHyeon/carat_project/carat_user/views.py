import json
import bcrypt  # 암호화 용
import jwt  # 토큰 발행용
from django.utils import timezone
import time
import random

from django.core.files import File
from carat_project.settings import SECRET_KEY  # 토큰 발행에 사용할 secret key
from .models import Users, Profiles
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage


def login_decorator(func):
    """ 로그인했는지 여부를 인증하는 데코레이터 """
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization', None)
            payload = jwt.decode(access_token, SECRET_KEY, algorithm='HS256')
            request.user = Users.objects.get(email=payload['email'])
        except jwt.exceptions.ExpiredSignatureError:
            return JsonResponse({'message': '토큰의 서명이 만료되었습니다!(Token expire.)'}, status=403)
        except jwt.exceptions.DecodeError:
            return JsonResponse({'message': '존재하지 않는 토큰 값입니다!(Token does not exist.)'}, status=401)
        except Users.DoesNotExist:
            return JsonResponse({'message': '토큰의 사용자 값이 존재하지 않습니다!(Account for token does not exist.)'}, status=404)
        return func(self, request, *args, **kwargs)
    return wrapper


class sign_up(View):
    def post(self, request):
        """ 계정 생성(회원 가입) """
        try:
            if not Users.objects.filter(email=request.POST['email']).exists():  # 존재하는 이메일인지 확인
                password = request.POST['password'].encode('utf-8')  # (비밀번호 암호화1) 입력된 패스워드를 바이트 형태로 인코딩
                password_crypt = bcrypt.hashpw(password, bcrypt.gensalt())  # (비밀번호 암호화2) 암호화된 비밀번호 생성
                password_crypt = password_crypt.decode('utf-8')  # (비밀번호 암호화3) DB에 저장할 수 있는 유니코드 문자열 형태로 디코딩
                users = Users(
                    email=request.POST['email'],
                    hashed_password=password_crypt,    # 암호화된 비밀번호를 저장
                    created_at=time.strftime('%Y-%m-%d %I:%M:%S', time.gmtime(timezone.now().timestamp())),
                )
                users.save()
                Profiles(
                    user_email=users,
                    name=request.POST['name'],
                    profile_image=f'images/profile/carrat_default_icon-0{random.randint(2, 5)}.png',
                    cover_image='images/profile/default_cover.jpg',
                    about_me='이곳에 자기소개를 입력하세요.',
                ).save()
                return HttpResponse(status=201)
            return JsonResponse({"message": "이미 존재하는 이메일 입니다!(That email is already in use.)"}, status=409)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!(a bad request.)"}, status=400)

    @login_decorator
    def delete(self, request):
        """ 계정 삭제(회원 탈퇴) """
        try:
            if Users.objects.filter(email=request.user.email).exists():
                target = Users.objects.get(email=request.user.email)
                # 삭제할 프로필의 사진들을 미디어 폴더에서 삭제
                for file in default_storage.listdir('images/profile/')[1]:
                    if target.email == file.split('-')[0]:
                        default_storage.delete('images/profile/' + file)
                Users.objects.filter(email=request.user.email).delete()
                return HttpResponse(status=204)
            return JsonResponse({'massage': '이미 존재하지 않는 유저 입니다!(The account does not exist.)'}, status=404)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!(a bad request.)"}, status=400)


class sign_in(View):
    def post(self, request):
        """ 로그인 (토큰 생성) """
        try:
            if Users.objects.filter(email=request.POST['email']).exists():
                if bcrypt.checkpw(request.POST['password'].encode('utf-8'),     # 비밀번호가 맞는지 검사
                                  Users.objects.get(email=request.POST['email']).hashed_password.encode('utf-8')):
                    # 토큰 생성 : jwt.encode({<유저정보>}, <시크릿키>, algorithm = '특정 알고리즘')
                    # jwt.encode로 jwt 토큰을 인코딩하고, 이것을 유니코드 문자열로 디코딩
                    access_token = jwt.encode({'token_type': 'access',
                                               'email': request.POST['email'],
                                               'exp': timezone.now().timestamp() + (3600 * 2),
                                               'iss': 'dong'},      # 토큰 발행자 : dong(김동현)
                                              SECRET_KEY, algorithm="HS256").decode('utf-8')
                    refresh_token = jwt.encode({'token_type': 'refresh',
                                                'email': request.POST['email'],
                                                'exp': timezone.now().timestamp() + (86400 * 7),    # (86400 * 7) == 7일
                                                'iss': 'dong'},     # 토큰 발행자 : dong(김동현)
                                               SECRET_KEY, algorithm="HS256").decode('utf-8')
                    return JsonResponse({"access_token": access_token, "refresh_token": refresh_token}, status=200)
                else:
                    return JsonResponse({"message": "비밀번호가 잘못되었습니다!(Email and password do not match.)"}, status=403)
            return JsonResponse({"message": "존재하지 않는 이메일입니다!(The account does not exist.)"}, status=400)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!(a bad request.)"}, status=400)

    @login_decorator
    def get(self, request):
        """ 토큰 갱신 """
        # 토큰 생성      jwt.encode({<유저정보>}, <시크릿키>, algorithm = '특정 알고리즘')
        access_token = jwt.encode({'token_type': 'access',
                                   'email': request.user.email,
                                   'exp': timezone.now().timestamp() + (3600 * 2),  # (3600 * 2) == 2시간
                                   'iss': 'dong'},  # 토큰 발행자 : dong(김동현)
                                  SECRET_KEY, algorithm="HS256").decode('utf-8')
        return JsonResponse({"access_token": access_token}, status=200)
