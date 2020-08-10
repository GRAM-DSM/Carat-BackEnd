from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view


# carat API
@api_view(['POST', 'DELETE'])
def do_carat(request):
    if request.method == 'POST':     # 캐럿(좋아요) 하기
        pass
    elif request.method == 'DELETE':    # 캐럿(좋아요) 취소
        pass


@api_view(['GET'])
def read_carat_list(request, id):       # 캐럿 리스트 가져오기
    pass


# caring API
@api_view(['POST'])
def create_caring(request):      # 캐링(트윗) 생성하기
    pass


@api_view(['GET', 'DELETE', 'PUT'])
def edit_caring(request, id):
    if request.method == 'GET':  # 캐링(트윗) 가져오기
        pass
    elif request.method == 'PUT':  # 캐링(트윗) 수정하기
        pass
    elif request.method == 'DELETE':  # 캐링(트윗) 삭제하기
        pass


# re-caring API
@api_view(['POST', 'DELETE'])
def do_recaring(request, id):
    if request.method == 'POST':  # 리캐링(리트윗) 생성하기
        pass
    elif request.method == 'DELETE':  # 리캐링(리트윗) 취소하기
        pass


# timeline API
@api_view(['GET'])
def read_timeline(request):      # 타임라인 가져오기
    pass


@api_view(['GET'])
def read_profile_timeline(request, email):    # 프로필 타임라인 가져오기
    pass
