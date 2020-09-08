from .core import *


class do_carat(View):
    @login_decorator
    def post(self, request, id):
        """ 캐럿 하기 """
        if not id.isdigit():     # 캐럿할 대상이 리캐링일 경우
            if Recarings.objects.filter(id=id).exists():
                id = Recarings.objects.get(id=id).caring.id
            else:
                return JsonResponse({'message': '캐럿할 리캐링이 존재하지 않습니다!(No recaring exists to carat.)!'}, status=404)
        if Carings.objects.filter(id=id).exists():
            if CaratList.objects.filter(carat_user_email=Users.objects.get(email=request.user.email),
                                        caring=Carings.objects.get(id=id)).exists():
                return JsonResponse({'message': '이미 이캐링에 캐럿하였습니다!'}, status=403)
            CaratList(carat_user_email=Users.objects.get(email=request.user.email),
                      caring=Carings.objects.get(id=id)
                      ).save()
            return HttpResponse(status=200)
        return JsonResponse({'message': '캐럿할 캐링이 존재하지 않습니다!(No caring exists to carat.)'}, status=404)

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
            if CaratList.objects.filter(carat_user_email=Users.objects.get(email=request.user.email), caring=Carings.objects.get(id=id)).exists():
                carat = CaratList.objects.filter(carat_user_email=Users.objects.get(email=request.user.email), caring=Carings.objects.get(id=id))
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
                }
                print(res)
                li.append(res)
            return JsonResponse({'result': li}, status=200)
        return JsonResponse({'message': '캐럿리스트를 볼 캐링이 존재하지 않습니다!'}, status=404)
