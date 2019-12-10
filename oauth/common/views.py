from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    if 'access_token' in request.session:
        return HttpResponse('Logged in')
    else:
        return HttpResponse('Not logged in')
