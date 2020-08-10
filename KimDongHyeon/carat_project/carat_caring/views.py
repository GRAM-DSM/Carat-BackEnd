from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view


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
