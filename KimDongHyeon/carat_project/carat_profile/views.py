from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def read_profile(request, email):
    pass


@api_view(['PUT'])
def update_profile(request):
    pass


@api_view(['GET'])
def following(request, email):
    pass


@api_view(['GET'])
def followers(request, email):
    pass
