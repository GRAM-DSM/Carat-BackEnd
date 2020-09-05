from django.core.files.storage import default_storage

from django.views import View
from .models import *
from carat_user.views import *
from carat_project.settings import SECRET_KEY, MEDIA_ROOT, MEDIA_URL  # 토큰 발행에 사용할 secret key, 이미지를 저장할 경로 MEDIA_ROOT
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from django.utils import timezone
import time


def caring_detail(request, id):
    """
    캐링/리캐링을 json 형태로 자세히 나타내는 함수
    :param request: 클라이언트가 요청(request)한 정보
    :param id: 자세히 나타낼 캐링/리캐링의 id 값
    :return: 자세히 나타낸 캐링/리캐링의 json 형태를 반환
    """
    if id.isdigit():  # 캐링일 경우
        if Carings.objects.filter(id=id).exists():
            target = Carings.objects.get(id=id)
            res = {
                'is_retweet': False,
                "caring_id": target.id,
                'owner': {
                    'name': Profiles.objects.get(user_email=target.user_email).name,
                    'email': target.user_email.email,
                    'profile_image': 'http://' + request.get_host() + MEDIA_URL
                                     + str(Profiles.objects.get(user_email=target.user_email).profile_image)
                },
                'post_time': target.created_at,
                'body': target.caring,
                'body_images': ['http://' + request.get_host() + MEDIA_URL + 'images/carings/' + url
                                for url in target.image.split(';') if url],
                'carat_count': CaratList.objects.filter(caring=target).count(),
                'retweet_count': Recarings.objects.filter(caring=target).count(),
                "am_i_recaring": Recarings.objects.filter(caring=target).filter(user_email=request.user.email).exists(),
                "am_i_carat": CaratList.objects.filter(caring=target).filter(carat_user_email=request.user.email).exists(),
            }
            print(res)
            print(res)
            return res
        return -1

    elif id[0] == 'r' and id[1:].isdigit():  # 리캐링일 경우
        if Recarings.objects.filter(id=id).exists():
            link = Recarings.objects.get(id=id)
            target = link.caring
            res = {
                'is_retweet': True,
                "recaring_name": Profiles.objects.get(user_email=link.user_email).name,
                "recaring_id": link.id,
                "caring_id": target.id,
                'owner': {
                    'name': Profiles.objects.get(user_email=target.user_email).name,
                    'email': target.user_email.email,
                    'profile_image': 'http://' + request.get_host() + MEDIA_URL
                                     + str(Profiles.objects.get(user_email=target.user_email).profile_image)
                },
                'post_time': target.created_at,
                'body': target.caring,
                'body_images': ['http://' + request.get_host() + MEDIA_URL + 'images/carings/' + url
                                for url in target.image.split(';') if url],
                'carat_count': CaratList.objects.filter(caring=target).count(),
                'retweet_count': Recarings.objects.filter(caring=target).count(),
                "am_i_recaring": Recarings.objects.filter(caring=target).filter(user_email=request.user.email).exists(),
                "am_i_carat": CaratList.objects.filter(caring=target).filter(carat_user_email=request.user.email).exists()
            }
            return res
        return -1


def file_upload(path, image_name, image):
    """
    장고의 미디어로 직접 파일을 저장하는 함수
    :param path: 저장할 파일의 경로 (/media/ 안의 세부적인 경로)
    :param image_name: 저장할 파일명
    :param image: 저장할 파일(이미지)
    :return: 성공적으로 저장된 파일의 경로를 반환
    """
    # 기존에 이미 같은 이름의 이미지 있을시 기존 이미지 삭제
    for file in default_storage.listdir(path)[1]:
        if image_name.split('.')[0] in file:
            default_storage.delete(path + file)
            break
    # 이미지 저장
    default_storage.save(path + image_name, image)
    return default_storage.url(image_name)


# caring API
# https://app.gitbook.com/@carat-1/s/gogo/1./undefined-1

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
            if CaratList.objects.filter(carat_user_email=request.user, caring=Carings.objects.get(id=id)).exists():
                return JsonResponse({'message': '이미 이캐링에 캐럿하였습니다!'}, status=400)
            CaratList(carat_user_email=request.user, caring=Carings.objects.get(id=id)).save()
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
            if CaratList.objects.filter(carat_user_email=request.user, caring=Carings.objects.get(id=id)).exists():
                carat = CaratList.objects.filter(carat_user_email=request.user, caring=Carings.objects.get(id=id))
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
                    follow_user_email=request.user
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


# timeline API
# https://app.gitbook.com/@carat-1/s/gogo/1./undefined

def timeline_detail(request, query_set, base_time, size):
    """
    타임라인의 캐링/리캐링의 자세한 정보를 각각 json으로 구해서 배열로 나타내는 함수
    :param request: 각각의 캐링/리캐링을 caring_detail 함수로 넘겨줄 때 인자값으로 사용
    :param query_set: 입력받는 전체 쿼리셋
    :param base_time: 뽑아낼 캐링/리캐링 배열의 기준이 되는 시각 값 (이 시각 이전에 생성된 캐링/리캐링을 기준으로 삼음)
    :param size: 캐링/리캐링 배열에서 몇개의 캐링/리캐링을 뽑아낼지 정해주는 값
    :return: 자세히 json 형태로 나타낸 캐링/리캐링 배열을 반환
    """
    if not query_set:
        return JsonResponse({'result': []}, status=200)
    timeline_list = list(sorted(query_set, key=lambda x: x.created_at, reverse=True))
    # base_time 이후에 나온 첫번째 캐링/리캐링 추출
    first_id = 0
    if base_time != '':
        for i, post in enumerate(timeline_list):
            if str(post.created_at) < base_time:
                first_id = i
                break
    # size 개수 만큼의 캐링/리캐링 추출 및, 각각 json 데이터로 리스트를 저장
    res_li = []
    for post in timeline_list[first_id: first_id + int(size)]:
        res_li.append(caring_detail(request=request, id=str(post.id)))
    return res_li


class read_timeline(View):
    @login_decorator
    def get(self, request):
        """ 타임라인 가져오기 """
        # 조건에 해당하는 쿼리셋 추출 + 정렬
        query_set = list(Carings.objects.all()) + list(Recarings.objects.all())
        result = timeline_detail(request=request, query_set=query_set, base_time=request.GET['base_time'], size=request.GET['size'])
        return JsonResponse({'result': result}, status=200)


class read_profile_caring_timeline(View):
    @login_decorator
    def get(self, request, email):
        """ 프로필에서 해당 유저의 캐링, 리캐링만 가져오기 """
        # 조건에 해당하는 쿼리셋 추출 + 정렬
        query_set = list(Carings.objects.filter(user_email=email)) + list(Recarings.objects.filter(user_email=email))
        result = timeline_detail(request=request, query_set=query_set, base_time=request.GET['base_time'], size=request.GET['size'])
        return JsonResponse({'result': result}, status=200)


class read_profile_carat_timeline(View):
    @login_decorator
    def get(self, request, email):
        """ 프로필에서 해당 유저가 캐럿한 캐링만 가져오기 """
        # 조건에 해당하는 쿼리셋 추출 + 정렬
        query_set = [query.caring for query in CaratList.objects.filter(carat_user_email=email)]
        result = timeline_detail(request=request, query_set=query_set, base_time=request.GET['base_time'], size=request.GET['size'])
        return JsonResponse({'result': result}, status=200)
