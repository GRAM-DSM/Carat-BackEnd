from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['POST', 'DELETE'])
def do_recaring(request, id):
    if request.method == 'POST':  # 리캐링(리트윗) 생성하기
        pass
    elif request.method == 'DELETE':  # 리캐링(리트윗) 취소하기
        pass
