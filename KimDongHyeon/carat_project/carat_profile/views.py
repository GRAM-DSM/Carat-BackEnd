from django.db import IntegrityError, OperationalError
from rest_framework.decorators import api_view
from .models import Profiles, Users, FollowList
from django.views import View

import jwt  # 토큰 발행용
from carat_project.settings import SECRET_KEY, MEDIA_ROOT, MEDIA_URL  # 토큰 발행에 사용할 secret key, 이미지를 저장할 경로 MEDIA_ROOT
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


class read_profile(View):
    @login_decorator
    def get(self, request, email):
        """ 유저의 프로필 정보 가져오기 """
        print('가져올 유저:', email)
        if Profiles.objects.filter(user_email=email).exists():
            profile = Profiles.objects.get(user_email=email)
            res = {
                "user_email": email,
                "name": profile.name,
                "about_me": profile.about_me,
                "profile_image_url": 'http://' + request.get_host() + MEDIA_URL + str(profile.profile_image),
                "cover_image_url": 'http://' + request.get_host() + MEDIA_URL + str(profile.cover_image),
                "following_count": len(FollowList.objects.filter(follow_user_email=email)),
                "follower_count": len(FollowList.objects.filter(followed_user_email=email)),
                "created_at": Users.objects.get(email=email).created_at,
                "my_self": (True if email == request.user.email else False)
            }
            print(res)
            return JsonResponse(res, status=200)
        return JsonResponse({'message': '해당 유저의 프로필을 찾을 수 없습니다!'}, status=403)


class update_profile(View):
    @login_decorator
    def post(self, request):
        """ 유저의 프로필 정보 수정하기 """
        try:
            print(request.user.email)
            if Profiles.objects.filter(user_email=request.user.email).exists():
                profile = Profiles.objects.get(user_email=request.user.email)
                print('name:', request.POST['name'],
                      'about_me:', request.POST['about_me'],
                      '\nprofile_image:', request.FILES['profile_image'],
                      '\ncover_image:', request.FILES['cover_image'])
                profile.name = request.POST['name']
                profile.about_me = request.POST['about_me']
                profile.profile_image = request.FILES['profile_image']
                profile.cover_image = request.FILES['cover_image']
                profile.save()
                return HttpResponse(status=200)
            return JsonResponse({'message': '해당 유저의 프로필이 존재하지 않습니다!'}, status=404)
        finally:
            pass


class following(View):
    @login_decorator
    def post(self, request, email):
        """ 팔로잉 하기 """
        try:
            print('팔로우 하는 사람:', request.user.email, '\n팔로우 받는 사람:', email)
            if request.user.email == email:
                return JsonResponse({'message': '자기자신을 팔로우 할 수 없습니다!'}, status=400)
            if Users.objects.filter(email=email).exists():
                if FollowList.objects.filter(
                    follow_user_email=Users.objects.get(email=request.user.email),
                    followed_user_email=Users.objects.get(email=email),
                ).exists():
                    return JsonResponse({'message': '이미 팔로우한 유저입니다!'}, status=400)
                FollowList(
                    follow_user_email=Users.objects.get(email=request.user.email),
                    followed_user_email=Users.objects.get(email=email),
                ).save()
                return HttpResponse(status=200)
            return JsonResponse({'message': '팔로우할 유저가 존재하지 않습니다!'}, status=400)
        except IntegrityError:
            return JsonResponse({'message': '이미 팔로우한 유저입니다!'}, status=400)

    @login_decorator
    def delete(self, request, email):
        """ 팔로잉 취소하기 """
        try:
            print('팔로우 취소 하는 사람:', request.user.email, '\n팔로우 취소 받는 사람:', email)
            if request.user.email == email:
                return JsonResponse({'message': '자기자신 입니다!'}, status=400)
            if Users.objects.filter(email=email).exists():
                if not FollowList.objects.filter(
                    follow_user_email=Users.objects.get(email=request.user.email),
                    followed_user_email=Users.objects.get(email=email),
                ).exists():
                    return JsonResponse({'message': '이미 팔로우가 되어있지 않습니다!'}, status=400)
                FollowList.objects.filter(
                    follow_user_email=Users.objects.get(email=request.user.email),
                    followed_user_email=Users.objects.get(email=email),
                ).delete()
                return HttpResponse(status=200)
            return JsonResponse({'message': '팔로우 취소할 유저가 존재하지 않습니다!'}, status=400)
        finally:
            pass

    @login_decorator
    def get(self, request, email):
        """ 팔로잉 목록 가져오기 """
        try:
            if Users.objects.filter(email=email).exists():
                followings = []
                for follow in FollowList.objects.filter(follow_user_email=Users.objects.get(email=email)):
                    profile = Profiles.objects.get(user_email=follow.followed_user_email)
                    is_following = FollowList.objects.filter(
                        followed_user_email=Users.objects.get(email=email),
                        follow_user_email=Users.objects.get(email=request.user.email)
                        ).exists()
                    res = {
                        'name': profile.name,
                        'email': profile.user_email.email,
                        'profile_image': 'http://' + request.get_host() + MEDIA_URL + str(profile.profile_image),
                        'is_follow': is_following
                    }
                    print(res)
                    followings.append(res)
                return JsonResponse({'followings:': followings}, status=200)
            return JsonResponse({'message': '해당 유저가 존재하지 않습니다!'}, status=400)
        finally:
            pass


class followers(View):
    @login_decorator
    def get(self, request, email):
        """ 팔로워 목록 가져오기 """
        try:
            if Users.objects.filter(email=email).exists():
                followings = []
                for follow in FollowList.objects.filter(followed_user_email=Users.objects.get(email=email)):
                    profile = Profiles.objects.get(user_email=follow.follow_user_email)
                    is_following = FollowList.objects.filter(
                        follow_user_email=Users.objects.get(email=email),
                        followed_user_email=Users.objects.get(email=request.user.email)
                        ).exists()
                    d = dict(zip(('profile_image', 'name', 'email', 'following',),
                             ('http://' + request.get_host() + MEDIA_URL + str(profile.profile_image),
                              profile.name, profile.user_email.email, is_following, )
                        ))
                    print(d)
                    followings.append(d)
                return JsonResponse({'followings:': followings}, status=200)
            return JsonResponse({'message': '해당 유저가 존재하지 않습니다!'}, status=400)
        finally:
            pass
