from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view

import jwt
from django.views import View
from .models import Profiles, Users, Carings, Recarings, CaratList, FollowList
from carat_project.settings import SECRET_KEY, MEDIA_ROOT, MEDIA_URL  # 토큰 발행에 사용할 secret key, 이미지를 저장할 경로 MEDIA_ROOT
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from django.utils import timezone
import time

# TODO 캐링 생성, 수정, 삭제 : 이미지 처리 안해줌
# TODO 캐링 자세히보기 ; 캐링, 리캐링 불러오기 안해줌
# TODO 타임라인 : 걍 안해줌


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


# caring API
# https://app.gitbook.com/@carat-1/s/gogo/1./undefined-1

class create_caring(View):
    @login_decorator
    def post(self, request):
        """ 캐링 생성하기 """
        print('게시자:', request.user.email, '본문:', request.POST['caring'])
        caring = Carings(
            user_email=Users.objects.get(email=request.user.email),
            caring=request.POST['caring'],
            image='',
            created_at=time.strftime('%Y-%m-%d %I:%M:%S', time.gmtime(timezone.now().timestamp())),
        )
        caring.save()
        return JsonResponse({'created_caring_id': caring.id}, status=200)


class edit_caring(View):
    @login_decorator
    def post(self, request, id):
        """ 캐링 수정하기 """
        try:
            if Carings.objects.filter(id=id).exists():
                target = Carings.objects.get(id=id)
                if target.user_email == Users.objects.get(email=request.user.email):
                    target.caring = request.POST.get('caring')
                    target.image = ''
                    target.save()
                    return HttpResponse(status=200)
                return JsonResponse({'message': '수정할 권한이 없습니다! (내가 생성한 캐링이 아님)'}, status=403)
            return JsonResponse({'message': '수정할 캐링이 존재하지 않습니다!'}, status=404)
        except KeyError:
            return JsonResponse({"message": "해당 캐링을 수정할 수 없습니다!"}, status=400)

    @login_decorator
    def delete(self, request, id):
        """ 캐링 삭제하기 """
        try:
            if Carings.objects.filter(id=id).exists():
                target = Carings.objects.get(id=id)
                if target.user_email == Users.objects.get(email=request.user.email):
                    target.caring = request.POST.get('caring')
                    print('삭제할 캐링:', target)
                    target.delete()
                    return HttpResponse(status=200)
                return JsonResponse({'message': '삭제할 권한이 없습니다! (내가 생성한 캐링이 아님)'}, status=403)
            return JsonResponse({'message': '삭제할 캐링이 존재하지 않습니다!'}, status=404)
        except KeyError:
            return JsonResponse({"message": "해당 캐링을 삭제할 수 없습니다!"}, status=400)


class detail_caring(View):
    @login_decorator
    def get(self, request, id):
        """ 캐링/리캐링 가져오기 """
        try:
            if id.isdigit():    # 캐링일 경우
                if Carings.objects.filter(id=id).exists():
                    target = Carings.objects.get(id=id)
                    res = {
                        'owner': {
                            'id': target.user_email.email,
                            'profile_image': 'http://' + request.get_host() + MEDIA_URL
                                             + str(Profiles.objects.get(user_email=target.user_email).profile_image)
                        },
                        'post_time': target.created_at,
                        'body': target.caring,
                        'body_images': [
                            ''
                        ],
                        'is_retweet': False,
                        'retweet_refer': None,
                        'carat_count': 0,
                        'retweet_count': 0
                    }
                return JsonResponse({'message': '자세히 볼 캐링이 존재하지 않습니다!'}, status=404)
            elif id.isdigit():    # 리캐링일 경우
                if Carings.objects.filter(id=id).exists():
                    target = Carings.objects.get(id=id)
                    res = {
                        'owner': {
                            'id': target.user_email.email,
                            'profile_image': 'http://' + request.get_host() + MEDIA_URL
                                             + str(Profiles.objects.get(user_email=target.user_email).profile_image)
                        },
                        'post_time': target.created_at,
                        'body': target.caring,
                        'body_images': [
                            ''
                        ],
                        'is_retweet': False,
                        'retweet_refer': None,
                        'carat_count': 0,
                        'retweet_count': 0
                    }
                return JsonResponse({'message': '자세히 볼 캐링이 존재하지 않습니다!'}, status=404)
        except KeyError:
            return JsonResponse({"message": "해당 캐링을 가져올 수 없습니다!"}, status=400)


# carat API
# https://app.gitbook.com/@carat-1/s/gogo/1./undefined-2

class do_carat(View):
    @login_decorator
    def post(self, request, id):
        """ 캐럿 하기 """
        if not id.isdigit():     # 캐럿할 대상이 리캐링일 경우
            if Recarings.objects.filter(id=id).exists():
                id = Recarings.objects.get(id=id).caring.id
            else:
                return JsonResponse({'message': '캐럿할 리캐링이 존재하지 않습니다!'}, status=404)
        if Carings.objects.filter(id=id).exists():
            print('캐럿대상 글:', id, ' 캐럿하는 사람:', request.user.email)
            if CaratList.objects.filter(
                carat_user_email=Users.objects.get(email=request.user.email),
                caring=Carings.objects.get(id=id)
            ).exists():
                return JsonResponse({'message': '이미 이캐링에 캐럿하였습니다!'}, status=400)
            CaratList(
                carat_user_email=Users.objects.get(email=request.user.email),
                caring=Carings.objects.get(id=id)
            ).save()
            return HttpResponse(status=200)
        return JsonResponse({'message': '캐럿할 캐링이 존재하지 않습니다!'}, status=404)

    @login_decorator
    def delete(self, request, id):
        """ 캐럿 취소 """
        if not id.isdigit():     # 캐럿할 대상이 리캐링일 경우
            if Recarings.objects.filter(id=id).exists():
                id = Recarings.objects.get(id=id).caring.id
            else:
                return JsonResponse({'message': '캐럿취소할 리캐링이 존재하지 않습니다!'}, status=404)
        if Carings.objects.filter(id=id).exists():
            print('캐럿취소대상 글:', id, ' 캐럿취소하는 사람:', request.user.email)
            if CaratList.objects.filter(
                carat_user_email=Users.objects.get(email=request.user.email),
                caring=Carings.objects.get(id=id)
            ).exists():
                carat = CaratList.objects.filter(
                    carat_user_email=Users.objects.get(email=request.user.email),
                    caring=Carings.objects.get(id=id)
                )
                print('삭제할 캐럿:', carat)
                carat.delete()
                return HttpResponse(status=200)
            return JsonResponse({'message': '이미 캐럿이 취소되어 있습니다!'}, status=400)
        return JsonResponse({'message': '캐럿취소할 캐링이 존재하지 않습니다!'}, status=404)


class read_carat_list(View):
    @login_decorator
    def get(self, request, id):
        """ 캐럿 리스트 가져오기 """
        if not id.isdigit():  # 캐럿할 대상이 리캐링일 경우
            if Recarings.objects.filter(id=id).exists():
                id = Recarings.objects.get(id=id).caring.id
            else:
                return JsonResponse({'message': '캐럿리스트를 볼 리캐링이 존재하지 않습니다!'}, status=404)
        if Carings.objects.filter(id=id).exists():
            print('id:', id)
            li = []
            for carat in CaratList.objects.filter(caring=Carings.objects.get(id=id)):
                profile = Profiles.objects.get(user_email=carat.carat_user_email)
                is_following = FollowList.objects.filter(
                    followed_user_email=carat.carat_user_email,
                    follow_user_email=Users.objects.get(email=request.user.email)
                ).exists()
                res = {
                    "name": profile.name,
                    "email": carat.carat_user_email.email,
                    "profile_image": 'http://' + request.get_host() + MEDIA_URL + str(profile.profile_image),
                    "is_follow": is_following
                },
                print(res)
                li.append(res)
            return JsonResponse({'result': li}, status=200)
        return JsonResponse({'message': '캐럿리스트를 볼 캐링이 존재하지 않습니다!'}, status=404)


# re-caring API
# https://app.gitbook.com/@carat-1/s/gogo/1./undefined-3

class create_recaring(View):
    @login_decorator
    def post(self, request):
        """ 리캐링 생성하기 """
        # 일단 리캐링의 id를 생성
        recaring_id = 'r1'
        if Recarings.objects.all().exists():
            recaring_id = f"r{int(Recarings.objects.order_by('-id')[0].id[1:])+1}"
            print('recaring_id:', recaring_id)
        # 그 후, 리캐링 생성
        if Carings.objects.filter(id=request.POST.get('id')).exists():
            recaring = Recarings(
                id=recaring_id,
                user_email=Users.objects.get(email=request.user.email),
                caring=Carings.objects.get(id=request.POST.get('id')),
                created_at=time.strftime('%Y-%m-%d %I:%M:%S', time.gmtime(timezone.now().timestamp()))
            )
            recaring.save()
            return JsonResponse({'created_recaring_id': recaring.id}, status=200)
        return JsonResponse({'message': '리캐링할 캐링이 존재하지 않습니다!'}, status=404)


class delete_recaring(View):
    @login_decorator
    def delete(self, request, id):
        """ 리캐링 취소하기 """
        if Recarings.objects.filter(id=id).exists():
            target = Recarings.objects.get(id=id)
            if target.user_email == Users.objects.get(email=request.user.email):
                print('취소할 리캐링:', target)
                target.delete()
                return HttpResponse(status=200)
            return JsonResponse({'message': '삭제할 권한이 없습니다! (내가 생성한 리캐링이 아님)'}, status=403)
        return JsonResponse({'message': '삭제할 리캐링이 존재하지 않습니다!'}, status=404)


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
