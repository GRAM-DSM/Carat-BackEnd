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
