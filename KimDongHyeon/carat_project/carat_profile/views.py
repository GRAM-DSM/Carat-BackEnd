from django.db import IntegrityError, OperationalError
from rest_framework.decorators import api_view
from .models import Profiles, Users, FollowList
from django.views import View

import jwt  # 토큰 발행용
from carat_project.settings import SECRET_KEY, MEDIA_ROOT, MEDIA_URL  # 토큰 발행에 사용할 secret key, 이미지를 저장할 경로 MEDIA_ROOT
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from carat_user.views import login_decorator
from carat_carat.views import file_upload


class read_profile(View):
    @login_decorator
    def get(self, request, email):
        """ 유저의 프로필 정보 가져오기 """
        try:
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
                return JsonResponse(res, status=200)
            return JsonResponse({'message': '프로필을 볼 계정이 존재하지 않음!(No account exists to view profile.)'}, status=404)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!(a bad request.)"}, status=400)


class update_profile(View):
    @login_decorator
    def post(self, request):
        """ 유저의 프로필 정보 수정하기 """
        try:
            if Profiles.objects.filter(user_email=request.user.email).exists():
                profile = Profiles.objects.get(user_email=request.user.email)
                profile.name = request.POST['name']
                profile.about_me = request.POST['about_me']
                # 프로필 이미지가 있으면 업데이트
                if 'profile_image' in request.FILES:
                    image = request.FILES['profile_image']
                    profile.profile_image = profile.user_email.email + '-profile.' + image.name.split('.')[-1]
                    file_upload('images/profile/', profile.profile_image, image)
                # 커버 이미지가 있으면 업데이트
                if 'cover_image' in request.FILES:
                    image = request.FILES['cover_image']
                    profile.cover_image = profile.user_email.email + '-cover.' + image.name.split('.')[-1]
                    file_upload('images/profile/', profile.cover_image, image)
                profile.save()
                return HttpResponse(status=201)
            return JsonResponse({'message': '프로필을 수정할 계정이 존재하지 않음!(No account exists to edit profile.)'}, status=404)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!(a bad request.)"}, status=400)


class following(View):
    @login_decorator
    def post(self, request, email):
        """ 팔로잉 하기 """
        try:
            if request.user.email == email:
                return JsonResponse({"message": "자기자신을 팔로우 할 수 없습니다!(You can't follow yourself.)"}, status=403)
            if Users.objects.filter(email=email).exists():
                if FollowList.objects.filter(
                    follow_user_email=Users.objects.get(email=request.user.email),
                    followed_user_email=Users.objects.get(email=email),
                ).exists():
                    return JsonResponse({'message': '이미 팔로우한 유저입니다!(Already Followed.)'}, status=409)
                FollowList(
                    follow_user_email=Users.objects.get(email=request.user.email),
                    followed_user_email=Users.objects.get(email=email),
                ).save()
                return HttpResponse(status=200)
            return JsonResponse({'message': '팔로우할 유저가 존재하지 않습니다!(No account exists to follow.)'}, status=404)
        except IntegrityError:
            return JsonResponse({'message': '이미 팔로우한 유저입니다!(Already Followed.)'}, status=409)

    @login_decorator
    def delete(self, request, email):
        """ 팔로잉 취소하기 """
        if request.user.email == email:
            return JsonResponse({'message': "자기자신을 언팔로우 할 수 없습니다!(You can't unfollow yourself.)"}, status=403)
        if Users.objects.filter(email=email).exists():
            if FollowList.objects.filter(
                follow_user_email=Users.objects.get(email=request.user.email),
                followed_user_email=Users.objects.get(email=email),
            ).exists():
                FollowList.objects.filter(
                    follow_user_email=Users.objects.get(email=request.user.email),
                    followed_user_email=Users.objects.get(email=email),
                ).delete()
                return HttpResponse(status=200)
            return JsonResponse({'message': '이미 팔로우가 되어있지 않습니다!(Not already followed.)'}, status=409)
        return JsonResponse({'message': '팔로우 취소할 유저가 존재하지 않습니다!(No account exists to unfollow.)'}, status=404)

    @login_decorator
    def get(self, request, email):
        """ 팔로잉 목록 가져오기 """
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
                followings.append(res)
            return JsonResponse({'followings:': followings}, status=200)
        return JsonResponse({'message': '팔로잉 목록을 볼 유저가 존재하지 않습니다!(No account exists to view follow-list.)'}, status=404)


class followers(View):
    @login_decorator
    def get(self, request, email):
        """ 팔로워 목록 가져오기 """
        if Users.objects.filter(email=email).exists():
            followings = []
            for follow in FollowList.objects.filter(followed_user_email=Users.objects.get(email=email)):
                profile = Profiles.objects.get(user_email=follow.follow_user_email)
                is_following = FollowList.objects.filter(
                    follow_user_email=Users.objects.get(email=email),
                    followed_user_email=Users.objects.get(email=request.user.email)
                    ).exists()
                res = {
                    'name': profile.name,
                    'email': profile.user_email.email,
                    'profile_image': 'http://' + request.get_host() + MEDIA_URL + str(profile.profile_image),
                    'is_follow': is_following
                }
                followings.append(res)
            return JsonResponse({'followings:': followings}, status=200)
        return JsonResponse({'message': '팔로워 목록을 볼 유저가 존재하지 않습니다!(No account exists to view follower-list.)'},
                            status=404)
