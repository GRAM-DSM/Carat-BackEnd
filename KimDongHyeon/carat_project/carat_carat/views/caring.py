from .core import *


class create_caring(View):
    @login_decorator
    def post(self, request):
        """ 캐링 생성하기 """
        print('게시자:', request.user.email, '본문:', request.POST['caring'])
        print('이미지:', request.FILES)
        caring = Carings(
            user_email=request.user,
            caring=request.POST['caring'],
            image='',
            created_at=time.strftime('%Y-%m-%d %I:%M:%S', time.gmtime(timezone.now().timestamp())),
        )
        caring.save()
        # 이미지 목록을 image 필드에 추가
        for i, image in request.FILES.items():
            image_url = file_upload('images/carings/', str(caring.id)+'-'+i[-1]+'.'+image.name.split('.')[-1], image)
            caring.image += str(caring.id)+'-'+i[-1]+'.'+image.name.split('.')[-1] + ';'
        caring.image = caring.image[:-1]
        caring.save()
        return JsonResponse({'created_caring_id': caring.id}, status=200)


class edit_caring(View):
    @login_decorator
    def post(self, request, id):
        """ 캐링 수정하기 """
        try:
            if Carings.objects.filter(id=id).exists():
                target = Carings.objects.get(id=id)
                if target.user_email == request.user:
                    target.caring = request.POST.get('caring')
                    # 일단 기존의 이미지 삭제
                    target.image = ''
                    for file in default_storage.listdir('images/carings/')[1]:
                        if str(target.id)+'-' in file:
                            default_storage.delete('images/carings/' + file)
                    # 새 이미지로 수정
                    for i, image in request.FILES.items():
                        image_url = file_upload('images/carings/',
                                                str(target.id) + '-' + i[-1] + '.' + image.name.split('.')[-1], image)
                        target.image += str(target.id) + '-' + i[-1] + '.' + image.name.split('.')[-1] + ';'
                    target.image = target.image[:-1]
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
                if target.user_email == request.user:
                    print('삭제할 캐링:', target)
                    for file in default_storage.listdir('images/carings/')[1]:
                        if str(target.id) == file.split('-')[0]:
                            default_storage.delete('images/carings/' + file)
                    target.delete()
                    return HttpResponse(status=200)
                return JsonResponse({'message': '삭제할 권한이 없습니다! (내가 생성한 캐링이 아님)'}, status=403)
            return JsonResponse({'message': '삭제할 캐링이 존재하지 않습니다!'}, status=404)
        except KeyError:
            return JsonResponse({"message": "해당 캐링을 삭제할 수 없습니다!"}, status=400)


class detail_caring(View):
    @login_decorator
    def get(self, request, id):
        """ 캐링/리캐링 가져오기(자세히보기) """
        try:
            res = caring_detail(request=request, id=id)
            print(res)
            if res == -1:
                return JsonResponse({'message': '해당 캐링을 찾을 수 없습니다!'}, status=404)
            return JsonResponse(res, status=200)
        except KeyError:
            return JsonResponse({"message": "해당 캐링을 가져올 수 없습니다!"}, status=400)

