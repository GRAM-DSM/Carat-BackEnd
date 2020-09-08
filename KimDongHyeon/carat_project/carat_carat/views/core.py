""" core.py는 다름아니라, carat_carat 의 여러 views.py 에서 공통으로 쓰이는 함수를 선언하거나, 공통으로 쓰이는 모듈을 임포트함 """
from django.core.files.storage import default_storage

from django.views import View
from carat_carat.models import *    # 1시간 버그의 지뢰, 배운점 : 커밋을 기능 개발마다 하고, 개발시 에러메시지가 답이 없으면, 문제없던 마지막 커밋으로 도로마무를 실용화 하자.
from carat_user.views import login_decorator
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
        if ''.join(image_name.split('.')[:-1]) in file:
            default_storage.delete(path + file)
            break
    # 이미지 저장
    default_storage.save(path + image_name, image)
    return default_storage.url(image_name)


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


# 이스터 에그?
class hi(View):
    def get(self, request):
        return JsonResponse({"hello!": "안녕하세요 :) 캐럿 서버 for Django(김동현 담당) 에 오신 것을 환영합니다!"},
                            json_dumps_params={'ensure_ascii': False}, status=200)
