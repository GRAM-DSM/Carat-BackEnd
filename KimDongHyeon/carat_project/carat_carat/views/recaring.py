from .core import *


class create_recaring(View):
    @login_decorator
    def post(self, request):
        """ 리캐링 생성하기 """
        # 일단 리캐링의 id를 생성
        recaring_id = ''
        if Recarings.objects.all().exists():
            recaring_id = f"r{int(Recarings.objects.order_by('-id')[0].id[1:])+1}"
            print('recaring_id:', recaring_id)
        # 그 후, 리캐링 생성
        if Carings.objects.filter(id=request.POST.get('id')).exists():
            recaring = Recarings(
                id=recaring_id,
                user_email=request.user,
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
            if target.user_email == request.user:
                print('취소할 리캐링:', target)
                target.delete()
                return HttpResponse(status=200)
            return JsonResponse({'message': '삭제할 권한이 없습니다! (내가 생성한 리캐링이 아님)'}, status=403)
        return JsonResponse({'message': '삭제할 리캐링이 존재하지 않습니다!'}, status=404)


class read_recaring_list(View):
    @login_decorator
    def get(self, request, id):
        """ 리캐링 리스트 가져오기 """
        if not id.isdigit():  # 리캐링 리스트를 볼 id가 리캐링일 경우 원본캐링으로 id를 추출
            if Recarings.objects.filter(id=id).exists():
                id = Recarings.objects.get(id=id).caring.id
            else:
                return JsonResponse({'message': '리캐링이 존재하지 않습니다!'}, status=404)
        if Carings.objects.filter(id=id).exists():
            print('id :', id)
            li = []
            for recaring in Recarings.objects.filter(caring=Carings.objects.get(id=id)):
                if li:  # 이미 리캐링한 사람이 리스트에 있으면 중복이므로 continue
                    if recaring.user_email.email in map(lambda x: x['email'], li):
                        continue
                profile = Profiles.objects.get(user_email=recaring.user_email)
                is_following = FollowList.objects.filter(
                    followed_user_email=recaring.user_email,
                    follow_user_email=Users.objects.get(email=request.user.email)
                ).exists()
                res = {
                    "name": profile.name,
                    "email": recaring.user_email.email,
                    "profile_image": 'http://' + request.get_host() + MEDIA_URL + str(profile.profile_image),
                    "is_follow": is_following
                }
                print(res)
                li.append(res)
            return JsonResponse({'result': li}, status=200)
        return JsonResponse({'message': '캐럿리스트를 볼 캐링이 존재하지 않습니다!'}, status=404)
