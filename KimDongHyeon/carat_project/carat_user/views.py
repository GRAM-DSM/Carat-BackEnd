import json
import bcrypt  # 암호화 용
import jwt  # 토큰 발행용
import time # 시간 지정용
from django.utils import timezone
import time

from carat_project.settings import SECRET_KEY  # 토큰 발행에 사용할 secret key
from .models import Users
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt


def login_decorator(func):
    """ 로그인했는지 여부를 인증하는 데코레이터 """
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization', None)
            payload = jwt.decode(access_token, SECRET_KEY, algorithm='HS256')
            user = Users.objects.get(email=payload['email'])
            request.user = user
        except jwt.exceptions.DecodeError:
            return JsonResponse({'message': '존재하지 않는 토큰 값입니다!'}, status=400)
        except Users.DoesNotExist:
            return JsonResponse({'message': '토큰의 사용자 값이 존재하지 않습니다!'}, status=400)

        return func(self, request, *args, **kwargs)
    return wrapper


class sign_up(View):
    def post(self, request):
        """ 계정 생성(회원 가입) """
        print('이메일 :', request.POST['email'], '\n비밀번호 :', request.POST['password'],
              '\n생성시간 :', time.strftime('%Y-%m-%d %I:%M:%S', time.gmtime(timezone.now().timestamp())))
        try:
            if Users.objects.filter(email=request.POST['email']).exists():  # 존재하는 이메일인지 확인
                return JsonResponse({"message": "이미 존재하는 이메일 입니다!(That email is already in use.)"}, status=409)

            password = request.POST['password'].encode('utf-8')  # (비밀번호 암호화1) 입력된 패스워드를 바이트 형태로 인코딩
            password_crypt = bcrypt.hashpw(password, bcrypt.gensalt())  # (비밀번호 암호화2) 암호화된 비밀번호 생성
            password_crypt = password_crypt.decode('utf-8')  # (비밀번호 암호화3) DB에 저장할 수 있는 유니코드 문자열 형태로 디코딩
            print(f'암호화 된 비밀번호 : {password_crypt}    비밀번호 길이 :', len(password_crypt))
            Users(
                email=request.POST['email'],
                hashed_password=password_crypt,    # 암호화된 비밀번호를 저장
                created_at=time.strftime('%Y-%m-%d %I:%M:%S', time.gmtime(timezone.now().timestamp())),
            ).save()
            return HttpResponse(status=200)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!(a bad request)"}, status=400)

    @login_decorator
    def delete(self, request):
        """ 계정 삭제(회원 탈퇴) """
        Users.objects.filter(email=request.user).delete()


class sign_in(View):
    def post(self, request):
        """ 로그인 (토큰 생성) """
        try:
            if Users.objects.filter(email=request.POST['email']).exists():
                if bcrypt.checkpw(request.POST['password'].encode('utf-8'),     # 비밀번호가 맞는지 검사
                                  Users.objects.get(email=request.POST['email']).hashed_password.encode('utf-8')):
                    # 토큰 생성 : jwt.encode({<유저정보>}, <시크릿키>, algorithm = '특정 알고리즘')
                    # jwt.encode로 jwt 토큰을 인코딩하고, 이것을 유니코드 문자열로 디코딩
                    token = jwt.encode({'email': request.POST['email']}, SECRET_KEY, algorithm="HS256").decode('utf-8')
                    return JsonResponse({"token": token}, status=200)
                else:
                    return JsonResponse({"message": "비밀번호가 잘못되었습니다!(Email and password do not match.)"}, status=403)
            return JsonResponse({"message": "존재하지 않는 이메일입니다!(The account does not exist.)"}, status=400)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!(a bad request)"}, status=400)

    @login_decorator
    def get(self, request):
        """ 토큰 갱신 """
        # 토큰 생성      jwt.encode({<유저정보>}, <시크릿키>, algorithm = '특정 알고리즘')
        token = jwt.encode({'email': request.user}, SECRET_KEY, algorithm="HS256")
        token = token.decode('utf-8')  # 유니코드 문자열로 디코딩
        return JsonResponse({"token": token}, status=200)


def hello(request):
    return JsonResponse({'haha': 'Do you know when I finish to develop server?'}, status=200)
