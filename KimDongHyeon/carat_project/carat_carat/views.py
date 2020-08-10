from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['POST', 'DELETE'])
def do_carat(request):
    if request.method == 'POST':     # 캐럿(좋아요) 하기
        pass
    elif request.method == 'DELETE':    # 캐럿(좋아요) 취소
        pass


@api_view(['GET'])
def read_carat_list(request, id):       # 캐럿 리스트 가져오기
    pass
