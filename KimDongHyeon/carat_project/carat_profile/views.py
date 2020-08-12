from rest_framework.decorators import api_view
from .models import Profiles, Users

import jwt  # 토큰 발행용
from carat_project.settings import SECRET_KEY  # 토큰 발행에 사용할 secret key
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


@api_view(['GET'])
def read_profile(request, email):
    """ 유저의 프로필 정보 가져오기 """
    print('가져올 유저:', email)
    if Profiles.objects.filter(user_email=email).exists():
        profile = Profiles.objects.get(user_email=email)
        print(profile.user_email, profile.name, profile.profile_image, profile.cover_image, profile.about_me)
        return JsonResponse({"user_email": email, "name": profile.name, "profile_image": profile.profile_image,
                             "cover_image": profile.cover_image, "about_me": profile.about_me}, status=200)
    return JsonResponse({'message': '해당 유저의 프로필을 찾을 수 없습니다!'}, status=403)


@api_view(['PUT'])
def update_profile(request):
    """ 유저의 프로필 정보 수정하기 """
    pass


@api_view(['GET'])
def following(request, email):      # 유저의 팔로잉 목록 가져오기
    pass


@api_view(['GET'])
def followers(request, email):      # 유저의 팔로워 목록 가져오기
    pass
