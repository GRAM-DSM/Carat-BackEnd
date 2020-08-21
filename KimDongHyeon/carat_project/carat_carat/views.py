from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view

import jwt
from django.views import View
from .models import Profiles, Users, Carings, Recarings, CaratList
from carat_project.settings import SECRET_KEY, MEDIA_ROOT, MEDIA_URL  # 토큰 발행에 사용할 secret key, 이미지를 저장할 경로 MEDIA_ROOT
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from django.utils import timezone
import time


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


# carat API
# https://app.gitbook.com/@carat-1/s/gogo/1./undefined-2

class do_carat(View):
    @login_decorator
    def post(self, request, id):
        """ 캐럿 하기 """
        print('게시자:', request.user.email, '본문:', request.POST['caring'])
        Carings(
            user_email=Users.objects.filter(email=request.user.email),
            caring=request.POST['caring'],
            image='',
            # carat_count=models.IntegerField(),
            # recaring_count=models.IntegerField(),
            created_at=time.strftime('%Y-%m-%d %I:%M:%S', time.gmtime(timezone.now().timestamp())),
        ).save()
        return JsonResponse({}, status=200)

    @login_decorator
    def delete(self, request, id):
        """ 캐럿 취소 """
        pass


class read_carat_list(View):
    @login_decorator
    def get(self, request):
        """ 캐럿 리스트 가져오기 """
        pass


# caring API
# https://app.gitbook.com/@carat-1/s/gogo/1./undefined-1

class create_caring(View):
    @login_decorator
    def post(self, request):
        """ 캐링 생성하기 """
        pass


class edit_caring(View):
    def get(self, request, id):
        """ 캐링 가져오기 """
        pass

    @login_decorator
    def put(self, request, id):
        """ 캐링 수정하기 """
        pass

    @login_decorator
    def delete(self, request, id):
        """ 캐링 삭제하기 """
        pass


# re-caring API
# https://app.gitbook.com/@carat-1/s/gogo/1./undefined-3

class do_recaring(View):
    @login_decorator
    def post(self, request, id):
        """ 리캐링 생성하기 """

    @login_decorator
    def delete(self, request, id):
        """ 리캐링 취소하기 """


# timeline API
# https://app.gitbook.com/@carat-1/s/gogo/1./undefined

class read_timeline(View):
    def get(self, request):
        """ 타임라인 가져오기 """
        pass


class read_profile_timeline(View):
    def get(self, request, email):
        """ 프로필 타임라인 가져오기 """
        pass
