import secrets
from urllib.parse import urlencode

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import requests


def github_api_request(url, post=False, access_token=None):
    headers = {
        'Accept': 'application/vnd.github.v3+json, application/json',
        'User-Agent': 'https://oauth-learning.com',
    }
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'
    if post:
        response = requests.post(url, data=post, headers=headers)
    else:
        response = requests.get(url, headers=headers)
    return response.json()


def login(request):
    request.session.flush()
    request.session['oauth_csrf'] = secrets.token_hex(16)

    query = urlencode({
        'response_type': 'code',
        'client_id': settings.GITHUB_CLIENT_ID,
        'redirect_uri': settings.BASE_URI,
        'scope': 'user public_repo',
        'state': request.session['oauth_csrf'],
    })
    url = f'{settings.GITHUB_AUTHORIZE_URL}?{query}'
    return redirect(url)


def home(request):
    context = {}
    if 'code' in request.GET:
        if request.GET.get('state') != request.session.get('oauth_csrf', 0):
            context['error'] = 'Invalid oauth state'
            return render(request, 'common/login.html', context)

        token = github_api_request(settings.GITHUB_TOKEN_URL, {
            'grant_type': 'authorization_code',
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'redirect_uri': settings.BASE_URI,
            'code': request.GET['code'],
        })
        # TODO: handle errors from GitHub
        request.session['access_token'] = token['access_token']

    if 'access_token' in request.session:
        return render(request, 'common/home.html')
    else:
        return render(request, 'common/login.html', context)
