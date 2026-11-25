import requests
import secrets
import string
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse

def generate_state():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def index(request):
    # Если SSO вернул ошибку в URL
    error = request.GET.get('error')
    error_description = request.GET.get('error_description')
    if error:
        return render(request, 'auth_app/index.html', {
            'error_msg': f"Ошибка SSO: {error}",
            'error_details': error_description
        })

    code = request.GET.get('code')
    state = request.GET.get('state')
    
    if not code:
        user_data = request.session.get('user_data')
        return render(request, 'auth_app/index.html', {'user_data': user_data})

    session_state = request.session.get('oauth_state')
    if not state or state != session_state:
        return render(request, 'auth_app/index.html', {'error_msg': 'Ошибка: Неверный параметр state (возможна атака MITM)'})

    # 1. Обмен кода на токен
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': settings.BMSTU_CLIENT_ID,
        'client_secret': settings.BMSTU_CLIENT_SECRET,
        'redirect_uri': settings.BMSTU_REDIRECT_URI,
    }
    
    response = requests.post(settings.BMSTU_TOKEN_URL, data=token_data)
    if response.status_code != 200:
        return render(request, 'auth_app/index.html', {
            'error_msg': 'Не удалось получить токен',
            'error_details': response.text
        })
    
    tokens = response.json()
    access_token = tokens.get('access_token')

    # 2. Получение данных пользователя
    headers = {'Authorization': f'Bearer {access_token}'}
    user_info_resp = requests.get(settings.BMSTU_USERINFO_URL, headers=headers)
    
    if user_info_resp.status_code != 200:
        return render(request, 'auth_app/index.html', {'error_msg': 'Не удалось получить данные пользователя'})
    
    user_data = user_info_resp.json()
    request.session['user_data'] = user_data
    request.session['access_token'] = access_token
    
    return redirect('/')

def sso_login(request):
    state = generate_state()
    request.session['oauth_state'] = state
    
    params = {
        'response_type': 'code',
        'client_id': settings.BMSTU_CLIENT_ID,
        'redirect_uri': settings.BMSTU_REDIRECT_URI,
        'state': state,
    }
    
    auth_url = f"{settings.BMSTU_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)

def sso_logout(request):
    access_token = request.session.get('access_token')
    
    if access_token:
        # Логаут на стороне сервера SSO
        headers = {'Authorization': f'Bearer {access_token}'}
        requests.get(settings.BMSTU_LOGOUT_URL, headers=headers)
    
    # Очистка локальной сессии
    request.session.flush()
    return redirect('/')
