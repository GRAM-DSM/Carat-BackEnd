import json
import bcrypt  # 암호화 용
import jwt  # 토큰 발행용
from django.utils import timezone
import time

from carat_project.settings import SECRET_KEY  # 토큰 발행에 사용할 secret key
from .models import Users, Profiles
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist


def login_decorator(func):
    """ 로그인했는지 여부를 인증하는 데코레이터 """
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization', None)
            payload = jwt.decode(access_token, SECRET_KEY, algorithm='HS256')
            request.user = Users.objects.get(email=payload['email'])
        except jwt.exceptions.ExpiredSignatureError:
            return JsonResponse({'message': '토큰의 서명이 만료되었습니다!'}, status=400)
        except jwt.exceptions.DecodeError:
            return JsonResponse({'message': '존재하지 않는 토큰 값입니다!'}, status=400)
        except Users.DoesNotExist:
            return JsonResponse({'message': '토큰의 사용자 값이 존재하지 않습니다!'}, status=400)

        return func(self, request, *args, **kwargs)
    return wrapper


class sign_up(View):
    def post(self, request):
        """ 계정 생성(회원 가입) """
        print('이메일 :', request.POST['email'],
              '\n비밀번호 :', request.POST['password'],
              '\n생성시간 :', time.strftime('%Y-%m-%d %I:%M:%S', time.gmtime(timezone.now().timestamp())))
        try:
            if Users.objects.filter(email=request.POST['email']).exists():  # 존재하는 이메일인지 확인
                return JsonResponse({"message": "이미 존재하는 이메일 입니다!(That email is already in use.)"}, status=409)

            password = request.POST['password'].encode('utf-8')  # (비밀번호 암호화1) 입력된 패스워드를 바이트 형태로 인코딩
            password_crypt = bcrypt.hashpw(password, bcrypt.gensalt())  # (비밀번호 암호화2) 암호화된 비밀번호 생성
            password_crypt = password_crypt.decode('utf-8')  # (비밀번호 암호화3) DB에 저장할 수 있는 유니코드 문자열 형태로 디코딩
            print(f'암호화 된 비밀번호 : {password_crypt}    비밀번호 길이 :', len(password_crypt))
            users = Users(
                email=request.POST['email'],
                hashed_password=password_crypt,    # 암호화된 비밀번호를 저장
                created_at=time.strftime('%Y-%m-%d %I:%M:%S', time.gmtime(timezone.now().timestamp())),
            )
            users.save()
            Profiles(
                user_email=users,
                name=request.POST['name'],
                profile_image='default_profile.jpg',
                cover_image='default_cover.jpg',
                about_me='이곳에 자기소개를 입력하세요.',
            ).save()
            return HttpResponse(status=200)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!(a bad request)"}, status=400)

    @login_decorator
    def delete(self, request):
        """ 계정 삭제(회원 탈퇴) """
        try:
            print('탈퇴하는 유저:', Users.objects.filter(email=request.user.email)[0].email)
            Profiles.objects.filter(user_email=request.user.email).delete()
            Users.objects.filter(email=request.user.email).delete()
            print('남은 유저:', Users.objects.all())
            return HttpResponse(status=200)
        except KeyError:
            return JsonResponse({"message": "해당 유저를 탈퇴할 수 없습니다!"}, status=400)


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
                                               'exp': timezone.now().timestamp() + (3600 * 2),      # (3600 * 2) == 2시간
                                               'iss': 'dong'},      # 토큰 발행자 : dong(김동현)
                                              SECRET_KEY, algorithm="HS256").decode('utf-8')
                    refresh_token = jwt.encode({'token_type': 'refresh',
                                                'email': request.POST['email'],
                                                'exp': timezone.now().timestamp() + (86400 * 7),    # (86400 * 7) == 7일
                                                'iss': 'dong'},     # 토큰 발행자 : dong(김동현)
                                               SECRET_KEY, algorithm="HS256").decode('utf-8')
                    print('엑세스 토큰:', access_token, '\n리플레시 토큰:', refresh_token)
                    return JsonResponse({"access_token": access_token, "refresh_token": refresh_token}, status=200)
                else:
                    return JsonResponse({"message": "비밀번호가 잘못되었습니다!(Email and password do not match.)"}, status=403)
            return JsonResponse({"message": "존재하지 않는 이메일입니다!(The account does not exist.)"}, status=400)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!(a bad request)"}, status=400)

    @login_decorator
    def get(self, request):
        """ 토큰 갱신 """
        # 토큰 생성      jwt.encode({<유저정보>}, <시크릿키>, algorithm = '특정 알고리즘')
        access_token = jwt.encode({'token_type': 'access',
                                   'email': request.user.email,
                                   'exp': timezone.now().timestamp() + (3600 * 2),  # (3600 * 2) == 2시간
                                   'iss': 'dong'},  # 토큰 발행자 : dong(김동현)
                                  SECRET_KEY, algorithm="HS256").decode('utf-8')
        print('새로 발급된 엑세스 토큰:', access_token)
        return JsonResponse({"token": access_token}, status=200)
