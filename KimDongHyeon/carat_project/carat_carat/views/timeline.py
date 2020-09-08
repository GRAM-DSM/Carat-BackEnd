from .core import *


class read_timeline(View):
    @login_decorator
    def get(self, request):
        """ 타임라인 가져오기 """
        try:
            # 조건에 해당하는 쿼리셋 추출 + 정렬
            query_set = list(Carings.objects.all()) + list(Recarings.objects.all())
            result = timeline_detail(request=request, query_set=query_set, base_time=request.GET['base_time'], size=request.GET['size'])
            return JsonResponse({'result': result}, status=200)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!(a bad request.)"}, status=400)


class read_profile_caring_timeline(View):
    @login_decorator
    def get(self, request, email):
        """ 프로필에서 해당 유저의 캐링, 리캐링만 가져오기 """
        try:
            if Users.objects.filter(email=email).exists():
                # 조건에 해당하는 쿼리셋 추출 + 정렬
                query_set = list(Carings.objects.filter(user_email=email)) + list(Recarings.objects.filter(user_email=email))
                result = timeline_detail(request=request, query_set=query_set, base_time=request.GET['base_time'], size=request.GET['size'])
                return JsonResponse({'result': result}, status=200)
            return JsonResponse({'message': '타임라인을 가져올 유저가 존재하지 않습니다!(Account does not exist to view the timeline!)'},
                                status=404)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!(a bad request.)"}, status=400)


class read_profile_carat_timeline(View):
    @login_decorator
    def get(self, request, email):
        """ 프로필에서 해당 유저가 캐럿한 캐링만 가져오기 """
        try:
            if Users.objects.filter(email=email).exists():
                # 조건에 해당하는 쿼리셋 추출 + 정렬
                query_set = [query.caring for query in CaratList.objects.filter(carat_user_email=email)]
                result = timeline_detail(request=request, query_set=query_set, base_time=request.GET['base_time'], size=request.GET['size'])
                return JsonResponse({'result': result}, status=200)
            return JsonResponse({'message': '타임라인을 가져올 유저가 존재하지 않습니다!(Account does not exist to view the timeline!)'},
                                status=404)
        except KeyError:
            return JsonResponse({"message": "key 값이 잘못되었습니다!(a bad request.)"}, status=400)
